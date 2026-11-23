/* ===== Practice shell for the Unix and Linux subject (assets/lxshell.js) =====
   A pretend Linux computer that lives only in the page. It has its own files, users and permissions, and a shell
   that understands the common commands, pipes, redirections, variables, globbing, quoting, and simple for, while
   and if blocks, so a learner can practise without any risk. Nothing here touches the reader's real computer.

   <div class="lx-term" data-lab='{"title": "...", "files": {"path": "text"}, "dirs": ["path"], "cwd": "~",
        "missions": [{"t": "what to do", "hint": "a command that does it", "check": [condition, ...]}]}'></div>

   A mission is done when all of its conditions hold after a command:
     {"cmd": "regex"}            the command line typed      {"out": "regex"}       the output of that command
     {"cwd": "/path"}            the current folder          {"exists": "path", "type": "f" | "d" | "l"}
     {"gone": "path"}            the path does not exist     {"has": ["path", "text"]}  the file contains the text
     {"mode": ["path", "755"]}   permission bits             {"lines": ["path", n]}     the file has n lines
     {"env": ["NAME", "value"]}  a shell variable            {"code": 0}            the exit status of the command
     {"envre": ["NAME", "regex"]} a variable matching a regex  {"exported": "NAME"}  the variable is exported
     {"alias": ["name", "text"]}  an alias with this text
   The engine (LXSH.World) has no DOM code, so tools can test it with node. ===== */
const LXSH = (() => {
  const USER = 'learner', HOST = 'brainy', HOME = '/home/learner';
  const T0 = Date.UTC(2026, 10, 23, 9, 30);   /* the starting files are dated 23 Nov 2026, 09:30 */
  const enc = s => new TextEncoder().encode(s).length;
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  /* ---------- the starting files ---------- */
  const SEED = {
    dirs: [['/bin', 0o755, 'root'], ['/boot', 0o755, 'root'], ['/dev', 0o755, 'root'], ['/etc', 0o755, 'root'], ['/home', 0o755, 'root'],
      [HOME, 0o750, USER], [HOME + '/logs', 0o755, USER], [HOME + '/scripts', 0o755, USER], [HOME + '/projects', 0o755, USER],
      [HOME + '/photos', 0o755, USER], ['/home/asha', 0o750, 'asha'], ['/opt', 0o755, 'root'], ['/proc', 0o555, 'root'], ['/root', 0o700, 'root'],
      ['/srv', 0o755, 'root'], ['/tmp', 0o1777, 'root'], ['/usr', 0o755, 'root'], ['/usr/bin', 0o755, 'root'], ['/usr/local', 0o755, 'root'],
      ['/usr/share', 0o755, 'root'], ['/var', 0o755, 'root'], ['/var/log', 0o755, 'root'], ['/var/www', 0o755, 'root'], ['/mnt', 0o755, 'root']],
    files: [
      [HOME + '/notes.txt', 'Buy milk\nCall grandma\nFinish the Linux lesson\n', 0o644],
      [HOME + '/fruits.txt', 'mango\napple\nbanana\napple\ncherry\nmango\napple\nkiwi\n', 0o644],
      [HOME + '/marks.csv', 'name,subject,score\nAsha,maths,91\nRavi,science,78\nMeera,maths,85\nJohn,english,67\nRavi,maths,72\nAsha,science,88\n', 0o644],
      [HOME + '/poem.txt', 'Twinkle twinkle little star\nHow I wonder what you are\nUp above the world so high\nLike a diamond in the sky\n', 0o644],
      [HOME + '/.bashrc', '# ~/.bashrc: read by every new interactive bash\nalias ll=\'ls -l\'\nexport EDITOR=nano\n', 0o644],
      [HOME + '/logs/app.log', '2026-11-23 09:00:01 INFO server started on port 8080\n2026-11-23 09:00:05 INFO user asha logged in\n2026-11-23 09:01:12 WARN disk 81% full\n2026-11-23 09:02:40 ERROR payment failed for order 1042\n2026-11-23 09:03:02 INFO user ravi logged in\n2026-11-23 09:04:18 ERROR database timeout after 30s\n2026-11-23 09:05:00 INFO backup finished\n', 0o644],
      [HOME + '/logs/old.log', '2026-11-22 23:59:59 INFO day closed\n', 0o644],
      [HOME + '/scripts/hello.sh', '#!/bin/bash\n# say hello to the person named in the first argument\nname=${1:-friend}\necho "Hello, $name!"\n', 0o644],
      [HOME + '/photos/beach.jpg', 'JPEGDATA', 0o644], [HOME + '/photos/cat.png', 'PNGDATA', 0o644],
      ['/home/asha/diary.txt', 'Private thoughts of Asha\n', 0o600, 'asha'],
      ['/etc/hostname', 'brainy\n', 0o644, 'root'],
      ['/etc/os-release', 'PRETTY_NAME="Practice Linux 1.0"\nNAME="Practice Linux"\nID=practice\nVERSION_ID="1.0"\n', 0o644, 'root'],
      ['/etc/passwd', 'root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\nasha:x:1001:1001:Asha Rao:/home/asha:/bin/bash\nlearner:x:1000:1000:Learner:/home/learner:/bin/bash\n', 0o644, 'root'],
      ['/etc/group', 'root:x:0:\nsudo:x:27:learner\nwww-data:x:33:\nlearner:x:1000:\nasha:x:1001:\n', 0o644, 'root'],
      ['/etc/shadow', 'root:*:20415:0:99999:7:::\nlearner:$y$j9T$demo$demo:20415:0:99999:7:::\n', 0o640, 'root'],
      ['/etc/hosts', '127.0.0.1 localhost\n127.0.1.1 brainy\n', 0o644, 'root'],
      ['/etc/fstab', '# <file system> <mount point> <type> <options> <dump> <pass>\nUUID=1b2c-77aa / ext4 defaults 0 1\n', 0o644, 'root'],
      ['/var/log/syslog', 'Nov 23 09:00:00 brainy systemd[1]: Started Daily apt download activities.\nNov 23 09:00:02 brainy CRON[812]: (root) CMD (run-parts /etc/cron.hourly)\n', 0o640, 'root'],
      ['/proc/version', 'Linux version 6.8.0-practice (practice@brainy) #1 SMP\n', 0o444, 'root'],
      ['/proc/cpuinfo', 'processor\t: 0\nmodel name\t: Practice CPU\ncpu cores\t: 2\nprocessor\t: 1\nmodel name\t: Practice CPU\ncpu cores\t: 2\n', 0o444, 'root'],
      ['/var/www/index.html', '<h1>It works</h1>\n', 0o644, 'root']
    ]
  };
  const CMDS = 'alias at atq atrm awk basename bash batch bg bunzip2 bzcat bzip2 cal cat cd chmod chown clear cp crontab cut date df diff dirname disown du echo env exit export expr false fg file find flock free grep groups gunzip gzip head help history hostname id jobs kill killall less ln ls man mkdir more mv nice nl nohup pgrep pkill printenv printf ps pwd renice readlink rev rm rmdir sed seq sh sleep sort source stat sudo tac tail tar tee test time top touch tr tree true type umask unalias uname uniq unset unxz unzip uptime wait wc which whoami xargs yes xz xzcat zcat zip'.split(' ');
  const BUILTIN = new Set('alias cd echo exit export help history pwd source test true false type umask unalias unset printf kill jobs read fg bg wait disown time declare typeset readonly set unset local shift let getopts mapfile readarray trap break continue return : eval shopt command'.split(' '));

  /* ---------- small helpers ---------- */
  function norm(path) {
    const out = [];
    path.split('/').forEach(p => { if (!p || p === '.') return; if (p === '..') out.pop(); else out.push(p); });
    return '/' + out.join('/');
  }
  const baseName = p => p === '/' ? '/' : p.replace(/\/+$/, '').split('/').pop();
  const dirName = p => { const s = p.replace(/\/+$/, ''); const i = s.lastIndexOf('/'); return i <= 0 ? '/' : s.slice(0, i); };
  const pad = (s, n, right) => { s = String(s); return s.length >= n ? s : right ? s + ' '.repeat(n - s.length) : ' '.repeat(n - s.length) + s; };
  const lines = s => { if (!s) return []; const a = s.split('\n'); if (a[a.length - 1] === '') a.pop(); return a; };
  const join = a => a.length ? a.join('\n') + '\n' : '';
  function globRe(g) {
    let r = '';
    for (let i = 0; i < g.length; i++) {
      const c = g[i];
      if (c === '*') r += '[^/]*';
      else if (c === '?') r += '[^/]';
      else if (c === '[') { const j = g.indexOf(']', i + 1); if (j < 0) { r += '\\['; continue; } let set = g.slice(i + 1, j); if (set[0] === '!') set = '^' + set.slice(1); r += '[' + set.replace(/\\/g, '\\\\') + ']'; i = j; }
      else r += c.replace(/[.+^${}()|\\]/g, '\\$&');
    }
    return new RegExp('^' + r + '$');
  }
  const hasGlob = s => /[*?[]/.test(s);
  /* the escapes of $'...' quoting, as listed under QUOTING in bash(1) */
  const ansiC = s => s.replace(/\\(x[0-9a-fA-F]{1,2}|[0-7]{1,3}|u[0-9a-fA-F]{1,4}|.)/g, (m, c) => {
    if (c[0] === 'x' && c.length > 1) return String.fromCharCode(parseInt(c.slice(1), 16));
    if (c[0] === 'u' && c.length > 1) return String.fromCharCode(parseInt(c.slice(1), 16));
    if (/^[0-7]+$/.test(c)) return String.fromCharCode(parseInt(c, 8));
    return { n: '\n', t: '\t', r: '\r', a: '\x07', b: '\b', e: '\x1b', E: '\x1b', f: '\f', v: '\v', '\\': '\\', "'": "'", '"': '"', '?': '?' }[c] ?? m;
  });
  function modeStr(n) {
    const t = n.type === 'd' ? 'd' : n.type === 'l' ? 'l' : n.type === 'c' ? 'c' : '-';
    const m = n.mode, b = (v, ch) => v ? ch : '-';
    let s = t;
    [[6, 0o4000, 's'], [3, 0o2000, 's'], [0, 0o1000, 't']].forEach(([sh, sp, ch]) => {
      const r = (m >> (sh + 2)) & 1, w = (m >> (sh + 1)) & 1, x = (m >> sh) & 1, spec = m & sp;
      s += b(r, 'r') + b(w, 'w') + (spec ? (x ? ch : ch.toUpperCase()) : b(x, 'x'));
    });
    return s;
  }
  function when(ms) {
    const d = new Date(ms);
    return `${MON[d.getUTCMonth()]} ${pad(d.getUTCDate(), 2)} ${pad(d.getUTCHours(), 2).replace(' ', '0')}:${pad(d.getUTCMinutes(), 2).replace(' ', '0')}`;
  }
  function human(n) {
    if (n < 1024) return String(n);
    const u = ['K', 'M', 'G', 'T']; let v = n, i = -1;
    while (v >= 1024 && i < 3) { v /= 1024; i++; }
    return (v < 10 ? Math.ceil(v * 10) / 10 : Math.ceil(v)) + u[i];
  }
  const REDIR_OPS = ['>', '>>', '>|', '<', '<<<', '2>', '2>>', '&>', '&>>', '2>&1', '>&2', '<<'];
  const UIDS = { root: 0, daemon: 1, 'www-data': 33, learner: 1000, asha: 1001 };

  /* ---------- the world: files, users and the shell state ---------- */
  class World {
    constructor(lab = {}) {
      this.root = { type: 'd', name: '/', mode: 0o755, owner: 'root', group: 'root', mtime: T0, kids: {} };
      SEED.dirs.forEach(([p, m, o]) => this.mk(p, 'd', m, o));
      SEED.files.forEach(([p, c, m, o]) => this.mk(p, 'f', m, o || USER, c));
      this.mk('/bin', 'l', 0o777, 'root', 'usr/bin', true);
      CMDS.forEach(c => this.mk('/usr/bin/' + c, 'f', 0o755, 'root', '#!practice ' + c + '\n'));
      this.mk('/usr/bin/passwd', 'f', 0o4755, 'root', '#!practice passwd\n');
      this.mk('/dev/null', 'c', 0o666, 'root', '');
      this.cwd = HOME;
      this.mk(HOME + '/latest.log', 'l', 0o777, USER, 'logs/app.log');
      (lab.dirs || []).forEach(p => this.mkdirs(this.abs(p)));
      Object.entries(lab.files || {}).forEach(([p, c]) => { const a = this.abs(p); this.mkdirs(dirName(a)); this.mk(a, 'f', /\.sh$/.test(a) && lab.exec ? 0o755 : 0o644, USER, c); });
      this.user = USER; this.cwd = lab.cwd ? this.abs(lab.cwd) : HOME; this.oldpwd = this.cwd;
      this.vars = { HOME, USER, LOGNAME: USER, SHELL: '/bin/bash', PATH: '/usr/local/bin:/usr/bin:/bin', PWD: this.cwd, LANG: 'C.UTF-8', HOSTNAME: HOST, EDITOR: 'nano', PS1: '\\u@\\h:\\w\\$ ', HISTSIZE: '1000', HISTFILESIZE: '2000', HISTFILE: HOME + '/.bash_history', OLDPWD: '', OPTIND: '1' };
      this.exported = new Set(['HOME', 'USER', 'LOGNAME', 'SHELL', 'PATH', 'PWD', 'LANG', 'EDITOR']);
      this.aliases = { ll: 'ls -l', la: 'ls -A' };
      this.hist = []; this.last = 0; this.umask = 0o022; this.args = []; this.clock = T0 + 60000; this.jobs = [];
      this.procs = [[1, 0, 'root', '/sbin/init', 'systemd'], [412, 1, 'root', 'sshd: /usr/sbin/sshd -D', 'sshd'], [618, 1, 'root', '/usr/sbin/cron -f', 'cron'], [905, 1, 'root', 'nginx: master process /usr/sbin/nginx', 'nginx'], [1200, 905, 'www-data', 'nginx: worker process', 'nginx'], [2001, 1, USER, '-bash', 'bash']].map(([pid, ppid, user, cmd, comm]) => ({ pid, ppid, user, cmd, comm, stat: 'S', ni: 0 }));
      this.nextPid = 2400;
    }
    now() { this.clock += 1000; return this.clock; }
    abs(p) { p = String(p); if (p === '~' || p.startsWith('~/')) p = HOME + p.slice(1); return norm(p.startsWith('/') ? p : this.cwd + '/' + p); }
    /* find a node. follow = true follows a symbolic link at the end of the path too */
    node(path, follow = true, depth = 0) {
      const parts = norm(path).split('/').filter(Boolean);
      let n = this.root, here = '/';
      for (let i = 0; i < parts.length; i++) {
        if (n.type === 'l') { n = this.node(n.target.startsWith('/') ? n.target : dirName(here) + '/' + n.target, true, depth + 1); if (!n) return null; }
        if (n.type !== 'd') return null;
        n = n.kids[parts[i]];
        if (!n) return null;
        here = norm(here + '/' + parts[i]);
      }
      if (follow && n.type === 'l' && depth < 8) return this.node(n.target.startsWith('/') ? n.target : dirName(here) + '/' + n.target, true, depth + 1);
      return n;
    }
    mk(path, type, mode, owner, content = '', link = false) {
      const p = norm(path), parent = this.node(dirName(p));
      const n = { type, name: baseName(p), mode, owner, group: owner, mtime: T0, kids: type === 'd' ? {} : undefined };
      if (type === 'l') n.target = content; else if (type !== 'd') n.data = content;
      parent.kids[n.name] = n;
      return n;
    }
    mkdirs(p) { let cur = ''; p.split('/').filter(Boolean).forEach(x => { cur += '/' + x; if (!this.node(cur)) this.mk(cur, 'd', 0o755, this.user); }); }
    /* permission check for the current user. root may do anything except run a file with no x bit */
    can(n, what) {
      const bit = { r: 4, w: 2, x: 1 }[what];
      if (this.user === 'root') return what !== 'x' || n.type === 'd' || (n.mode & 0o111) !== 0;
      const sh = n.owner === this.user ? 6 : this.inGroup(n.group) ? 3 : 0;
      return ((n.mode >> sh) & bit) !== 0;
    }
    inGroup(g) { if (g === this.user) return true; const row = (this.node('/etc/group').data || '').split('\n').find(l => l.startsWith(g + ':')); return !!row && row.split(':')[3].split(',').includes(this.user); }
    size(n) { if (n.type === 'f' && n.data && n.data.charCodeAt(0) === 0 && this.unpack && this.unpack(n.data)) return this.unpack(n.data).size; return n.type === 'd' ? 4096 : n.type === 'l' ? n.target.length : n.type === 'c' ? 0 : enc(n.data); }
    tilde(p) { return p === HOME ? '~' : p.startsWith(HOME + '/') ? '~' + p.slice(HOME.length) : p; }
    prompt() { return { user: this.user, host: HOST, dir: this.tilde(this.cwd), sign: this.user === 'root' ? '#' : '$' }; }

    /* ---------- reading the command line ---------- */
    /* splits a line into words and operators. A word keeps a list of parts: {t: text, q: 0 none | 1 single | 2 double} */
    lex(src) {
      const toks = []; let i = 0, w = null, wl = 1, cp = 0, cl = 1;
      /* the line number of position pos. Positions only grow, so counting goes on from the last call */
      const lineAt = pos => { while (cp < pos && cp < src.length) { if (src[cp] === '\n') cl++; cp++; } return cl; };
      const push = (t, q) => { if (!w) { w = { parts: [] }; wl = lineAt(i); } w.parts.push({ t, q }); };
      const end = () => { if (w) { toks.push({ w, ln: wl }); w = null; } };
      const tp = toks.push.bind(toks);
      toks.push = (...xs) => tp(...xs.map(x => (x.ln === undefined && (x.ln = x.w ? wl : lineAt(i)), x)));
      while (i < src.length) {
        const c = src[i];
        if (c === ' ' || c === '\t') { end(); i++; continue; }
        if (c === '\n') { end(); toks.push({ op: ';' }); i++; continue; }
        if (c === '#' && !w) { while (i < src.length && src[i] !== '\n') i++; continue; }
        if (!w && src.startsWith('((', i)) { const k = this.matchArith(src, i + 2); toks.push({ op: '((', text: src.slice(i + 2, k) }); i = k + 2; continue; }
        if (!w && src.startsWith('[[', i) && /\s/.test(src[i + 2] || '')) { const k = this.matchDbl(src, i + 2); toks.push({ op: '[[', text: src.slice(i + 2, k) }); i = k + 2; continue; }
        if (c === '(' && w && w.parts.every(p => !p.q) && /^[A-Za-z_]\w*(\[[^\]]*\])?\+?=$/.test(w.parts.map(p => p.t).join(''))) {
          const k = this.matchParen(src, i); push('(' + src.slice(i + 1, k) + ')', 0); w.parts[w.parts.length - 1].arr = src.slice(i + 1, k); i = k + 1; continue;
        }
        if (c === '$' && src[i + 1] === "'") { let j = i + 2, s = ''; while (j < src.length && src[j] !== "'") { if (src[j] === '\\' && j + 1 < src.length) { s += src[j] + src[j + 1]; j += 2; continue; } s += src[j++]; } if (j >= src.length) throw new Error('unexpected end of line, a quote was not closed'); push(ansiC(s), 1); i = j + 1; continue; }
        if (c === '`') { const j = src.indexOf('`', i + 1); if (j < 0) throw new Error('unexpected end of line, a ` was not closed'); push('$(' + src.slice(i + 1, j) + ')', 0); i = j + 1; continue; }
        if ((c === '<' || c === '>') && src[i + 1] === '(') { const k = this.matchParen(src, i + 1); if (c === '>') throw new Error('>( ) is not available in the practice shell, only <( )'); if (!w) w = { parts: [] }; w.parts.push({ t: src.slice(i + 2, k), q: 0, ps: true }); i = k + 1; continue; }
        if (c === "'") { const j = src.indexOf("'", i + 1); if (j < 0) throw new Error('unexpected end of line, a quote was not closed'); push(src.slice(i + 1, j), 1); i = j + 1; continue; }
        if (c === '"') {
          let j = i + 1, s = '';
          while (j < src.length && src[j] !== '"') {
            if (src[j] === '\\' && '"\\$`'.includes(src[j + 1])) { s += src[j] + src[j + 1]; j += 2; continue; }
            if (src[j] === '$' && src[j + 1] === '(') { const k = this.matchParen(src, j + 1); s += src.slice(j, k + 1); j = k + 1; continue; }
            if (src[j] === '`') { const k = src.indexOf('`', j + 1); if (k < 0) throw new Error('unexpected end of line, a ` was not closed'); s += '$(' + src.slice(j + 1, k) + ')'; j = k + 1; continue; }
            s += src[j++];
          }
          if (j >= src.length) throw new Error('unexpected end of line, a quote was not closed');
          push(s, 2); i = j + 1; continue;
        }
        if (c === '\\') { push(src[i + 1] || '', 1); i += 2; continue; }
        if (c === '$' && src[i + 1] === '(') { const k = this.matchParen(src, i + 1); push(src.slice(i, k + 1), 0); i = k + 1; continue; }
        if (c === '$' && src[i + 1] === '{') { const k = src.indexOf('}', i); push(src.slice(i, k + 1), 0); i = k + 1; continue; }
        const two = src.slice(i, i + 2), three = src.slice(i, i + 4);
        if (three === '2>&1') { end(); toks.push({ op: '2>&1' }); i += 4; continue; }
        if (three === '1>&2' && !w) { toks.push({ op: '>&2' }); i += 4; continue; }
        if (src.startsWith('>&2', i)) { end(); toks.push({ op: '>&2' }); i += 3; continue; }
        if (src.startsWith('<<<', i)) { end(); toks.push({ op: '<<<' }); i += 3; continue; }
        if (src.startsWith('&>>', i)) { end(); toks.push({ op: '&>>' }); i += 3; continue; }
        if (two === '>|') { end(); toks.push({ op: '>|' }); i += 2; continue; }
        if (c === '1' && !w && src[i + 1] === '>') { i++; continue; }
        if (['&&', '||', '>>', '&>', '2>', '<<'].includes(two)) {
          if (two === '2>' && w) { push('2', 0); push('>', 0); i += 2; continue; }
          end();
          if (two === '2>' && src[i + 2] === '>') { toks.push({ op: '2>>' }); i += 3; continue; }
          if (two === '<<') { const m = /^<<-?\s*['"]?(\w+)['"]?/.exec(src.slice(i)); if (m) { toks.push({ op: '<<', tag: m[1] }); i += m[0].length; continue; } }
          toks.push({ op: two }); i += 2; continue;
        }
        if ('|;&<>'.includes(c)) { end(); toks.push({ op: c }); i++; continue; }
        if (c === '(' || c === ')') { end(); toks.push({ op: c }); i++; continue; }
        let j = i, s = '';
        while (j < src.length && !" \t\n'\"\\|;&<>`".includes(src[j]) && !(src[j] === '$' && (src[j + 1] === '(' || src[j + 1] === '{')) && !(src[j] === '(' || src[j] === ')')) s += src[j++];
        push(s, 0); i = j;
      }
      end();
      return toks;
    }
    /* the text of a word as it was typed, quotes included, for BASH_COMMAND and set -x style messages */
    srcText(w) { return w.parts.map(p => p.q === 1 ? `'${p.t}'` : p.q === 2 ? `"${p.t}"` : p.t).join(''); }
    /* the end of (( ... )): the first )) that closes the brackets opened inside */
    matchArith(s, i) { let d = 0; for (let j = i; j < s.length; j++) { if (s[j] === '(') d++; else if (s[j] === ')') { if (!d && s[j + 1] === ')') return j; d--; } } throw new Error('syntax error: (( was not closed with ))'); }
    /* the end of [[ ... ]]: a ]] that stands on its own, outside quotes */
    matchDbl(s, i) {
      for (let j = i; j < s.length; j++) {
        if (s[j] === "'") { j = s.indexOf("'", j + 1); if (j < 0) break; continue; }
        if (s[j] === '"') { j++; while (j < s.length && s[j] !== '"') { if (s[j] === '\\') j++; j++; } continue; }
        if (s[j] === '\\') { j++; continue; }
        if (s.startsWith(']]', j) && /\s/.test(s[j - 1]) && (j + 2 >= s.length || /[\s;&|)]/.test(s[j + 2]))) return j;
      }
      throw new Error('syntax error, ]] is missing');
    }
    matchParen(s, i) { let d = 0; for (let j = i; j < s.length; j++) { if (s[j] === '(') d++; else if (s[j] === ')') { d--; if (!d) return j; } } throw new Error('a ( was not closed'); }
    wordText(w) { return w.parts.map(p => p.t).join(''); }

    /* ---------- parsing into a small tree ---------- */
    parse(toks) {
      let i = 0;
      const peekW = () => toks[i] && toks[i].w && !toks[i].w.parts.some(p => p.q) ? this.wordText(toks[i].w) : null;
      const isOp = o => toks[i] && toks[i].op === o;
      const skipSep = () => { while (toks[i] && (toks[i].op === ';' || toks[i].op === '\n')) i++; };
      const expectWord = kw => { skipSep(); if (!toks[i]) { const e = new Error('syntax error: unexpected end of file'); e.eof = true; throw e; } if (peekW() !== kw) throw new Error(`syntax error: expected "${kw}"`); i++; };
      const list = stop => {
        const items = [];
        skipSep();
        while (i < toks.length && !(peekW() && stop.includes(peekW())) && !isOp(')')) {
          const p = andor();
          let bg = false;
          if (isOp('&')) { bg = true; i++; }
          items.push({ p, bg });
          skipSep();
        }
        return { t: 'list', items };
      };
      const andor = () => {
        let left = pipeline();
        while (isOp('&&') || isOp('||')) { const op = toks[i++].op; skipSep(); left = { t: op === '&&' ? 'and' : 'or', a: left, b: pipeline() }; }
        return left;
      };
      const pipeline = () => {
        let neg = false;
        if (peekW() === '!') { neg = true; i++; }
        const cmds = [command()];
        while (isOp('|')) { i++; skipSep(); cmds.push(command()); }
        return { t: 'pipe', cmds, neg };
      };
      const command = () => {
        const kw = peekW();
        if (kw === 'for' && toks[i + 1] && toks[i + 1].op === '((') {
          i++; const parts = toks[i++].text.split(';'); if (parts.length !== 3) throw new Error('syntax error: for (( needs three parts split by ;'); skipSep();
          expectWord('do'); const body = list(['done']); expectWord('done');
          return { t: 'cfor', a: parts[0], b: parts[1], c: parts[2], body, redir: redirs() };
        }
        if (isOp('((')) { const e = toks[i++].text; return { t: 'arith', e, redir: redirs() }; }
        if (isOp('[[')) { const text = toks[i++].text; return { t: 'dbl', text, redir: redirs() }; }
        if (kw === 'for') {
          i++; const v = this.wordText(toks[i++].w); let words = [];
          skipSep();
          if (peekW() === 'in') { i++; while (toks[i] && toks[i].w && peekW() !== 'do') words.push(toks[i++].w); }
          else words = null;
          expectWord('do'); const body = list(['done']); expectWord('done');
          return { t: 'for', v, words, body, redir: redirs() };
        }
        if (kw === 'while' || kw === 'until') {
          i++; const cond = list(['do']); expectWord('do'); const body = list(['done']); expectWord('done');
          return { t: 'while', until: kw === 'until', cond, body, redir: redirs() };
        }
        if (kw === 'if') {
          i++; const arms = []; let els = null;
          const cond = list(['then']); expectWord('then'); arms.push([cond, list(['elif', 'else', 'fi'])]);
          while (peekW() === 'elif') { i++; const c = list(['then']); expectWord('then'); arms.push([c, list(['elif', 'else', 'fi'])]); }
          if (peekW() === 'else') { i++; els = list(['fi']); }
          expectWord('fi');
          return { t: 'if', arms, els, redir: redirs() };
        }
        if (kw === 'case') {
          i++; const word = toks[i++].w; expectWord('in'); const arms = [];
          skipSep();
          while (peekW() !== 'esac' && i < toks.length) {
            if (isOp('(')) i++;
            const pats = [];
            while (toks[i] && !isOp(')')) { if (isOp('|')) { i++; continue; } pats.push(toks[i++].w); }
            i++;
            const body = { t: 'list', items: [] };
            skipSep();
            const armEnd = () => isOp(';') && toks[i + 1] && (toks[i + 1].op === ';' || toks[i + 1].op === '&');
            while (i < toks.length && !armEnd() && peekW() !== 'esac') { const p = andor(); body.items.push({ p }); if (isOp(';') && !armEnd()) i++; skipSepSingle(); }
            let fall = '';
            if (armEnd()) { if (toks[i + 1].op === '&') { fall = ';&'; i += 2; } else { i += 2; if (isOp('&')) { fall = ';;&'; i++; } } }
            arms.push([pats, body, fall]); skipSep();
          }
          expectWord('esac');
          return { t: 'case', word, arms };
        }
        if (isOp('(')) { i++; const body = list([]); if (!isOp(')')) throw new Error('syntax error: ( was not closed'); i++; return { t: 'sub', body, redir: redirs() }; }
        const kwFn = kw === 'function' && toks[i + 1] && toks[i + 1].w;
        if (kwFn || (toks[i] && toks[i].w && toks[i + 1] && toks[i + 1].op === '(' && toks[i + 2] && toks[i + 2].op === ')')) {
          if (kwFn) i++;
          const name = this.wordText(toks[i].w); i++;
          if (isOp('(') && toks[i + 1] && toks[i + 1].op === ')') i += 2;
          skipSep();
          if (peekW() !== '{') throw new Error('syntax error: a function body starts with {');
          i++; const inner = list(['}']); expectWord('}');
          /* redirections written after the closing brace apply every time the function runs */
          return { t: 'fn', name, body: { t: 'sub', body: inner, keep: true, redir: redirs() } };
        }
        if (kw === '{') { i++; const body = list(['}']); expectWord('}'); return { t: 'sub', body, keep: true, redir: redirs() }; }
        const words = [], redir = [], start = toks[i];
        while (i < toks.length) {
          const tk = toks[i];
          if (tk.w) { words.push(tk.w); i++; continue; }
          if (REDIR_OPS.includes(tk.op)) { redir.push(redirOne()); continue; }
          break;
        }
        if (!words.length && !redir.length) throw new Error(`syntax error near "${toks[i] ? toks[i].op || this.wordText(toks[i].w) : 'end of line'}"`);
        return { t: 'cmd', words, redir, ln: start && start.ln };
      };
      const skipSepSingle = () => { while (toks[i] && toks[i].op === ';' && !(toks[i + 1] && (toks[i + 1].op === ';' || toks[i + 1].op === '&'))) i++; };
      const redirOne = () => {
        const tk = toks[i++];
        if (tk.op === '2>&1' || tk.op === '>&2') return { op: tk.op };
        if (tk.op === '<<') { return { op: '<<', tag: tk.tag }; }
        if (!toks[i] || !toks[i].w) throw new Error('syntax error: a file name is needed after ' + tk.op);
        return { op: tk.op, w: toks[i++].w };
      };
      const redirs = () => { const r = []; while (toks[i] && REDIR_OPS.includes(toks[i].op) && toks[i].op !== '<<') r.push(redirOne()); return r; };
      const tree = list([]);
      if (i < toks.length) throw new Error(`syntax error near "${toks[i].op || this.wordText(toks[i].w)}"`);
      return tree;
    }

    /* ---------- expansions ---------- */
    param(name, soft) {
      if (name === '?') return String(this.last);
      if (name === '#') return String(this.args.length);
      if (name === '@') return this.args.join(' ');
      if (name === '*') return this.args.join(this.ifsJoin());
      if (name === '$') return '2001';
      if (name === '!') return this.lastBg ? String(this.lastBg) : '';
      if (name === '0') return this.script || 'bash';
      if (/^\d+$/.test(name)) return this.args[+name - 1] ?? '';
      if (name === 'RANDOM') return String(Math.floor(Math.random() * 32768));
      if (name === 'PWD') return this.cwd;
      if (name === 'BASH_COMMAND') return this.bashCmd || '';
      if (!(name in this.vars) && this.arrays && this.arrays[name] !== undefined && name !== 'PIPESTATUS') { const A = this.arrays[name]; return (Array.isArray(A) ? A[0] : A['0']) ?? ''; }
      if (!(name in this.vars) && this.opts && this.opts.nounset && !soft) throw new Error(`${name}: unbound variable`);
      return this.vars[name] ?? '';
    }
    braceParam(body) {
      let m;
      const A = this.arrays || {};
      if ((m = /^!(\w+)[*@]$/.exec(body))) return Object.keys(this.vars).concat(Object.keys(A)).filter((k, ix, all) => k.startsWith(m[1]) && all.indexOf(k) === ix).sort().join(' ');
      if ((m = /^!(\w+)$/.exec(body))) { const t = this.param(m[1]); return t ? this.braceParam(t) : ''; }
      if ((m = /^#(\w+)\[[@*]\]$/.exec(body))) return String(this.arrVals(m[1]).length);
      if ((m = /^!(\w+)\[[@*]\]$/.exec(body))) return this.arrKeys(m[1]).join(' ');
      if ((m = /^(\w+)\[[@*]\]:(-?\d+)(?::(\d+))?$/.exec(body))) { const v = this.arrVals(m[1]); let st = +m[2]; if (st < 0) st = Math.max(0, v.length + st); return (m[3] !== undefined ? v.slice(st, st + +m[3]) : v.slice(st)).join(' '); }
      if ((m = /^(\w+)\[([@*])\]$/.exec(body))) return this.arrVals(m[1]).join(m[2] === '*' ? this.ifsJoin() : ' ');
      if ((m = /^(\w+\[[@*]\]|[@*])(\/\/?|##?|%%?|\^\^?|,,?)(.*)$/.exec(body))) {
        const all = m[1].length === 1 ? this.args : this.arrVals(m[1].slice(0, -3)), star = m[1].endsWith('*') || m[1] === '*';
        const keep = this.vars.__el; let out;
        try { out = all.map(x => { this.vars.__el = x; return this.braceParam('__el' + m[2] + m[3]); }); } finally { if (keep === undefined) delete this.vars.__el; else this.vars.__el = keep; }
        return out.join(star ? this.ifsJoin() : ' ');
      }
      if ((m = /^#(\w+)\[(.+)\]$/.exec(body))) return String(this.arrGet(m[1], m[2]).length);
      if ((m = /^(\w+)\[(.+)\]$/.exec(body))) return this.arrGet(m[1], m[2]);
      if ((m = /^@:(\d+)(?::(\d+))?$/.exec(body))) { const all = [this.script || 'bash'].concat(this.args); return (m[2] !== undefined ? all.slice(+m[1], +m[1] + +m[2]) : all.slice(+m[1])).join(' '); }
      if ((m = /^([*@])(\^\^|,,|\^|,)$/.exec(body))) { const t = { '^^': x => x.toUpperCase(), ',,': x => x.toLowerCase(), '^': x => x && x[0].toUpperCase() + x.slice(1), ',': x => x && x[0].toLowerCase() + x.slice(1) }[m[2]]; return this.args.map(t).join(' '); }
      if ((m = /^(\w+)(\^|,)$/.exec(body))) { const v = this.param(m[1]); return v ? (m[2] === '^' ? v[0].toUpperCase() : v[0].toLowerCase()) + v.slice(1) : v; }
      if ((m = /^#(\w+|@)$/.exec(body))) return String(m[1] === '@' ? this.args.length : this.param(m[1]).length);
      if ((m = /^(\w+|\d+)(:?[-=+?])(.*)$/.exec(body))) {
        const v = this.param(m[1], true), set = m[2].includes(':') ? v !== '' : (m[1] in this.vars || /^\d+$/.test(m[1]) && this.args.length >= +m[1]);
        const op = m[2].replace(':', ''), word = this.expandStr(m[3]);
        if (op === '-') return set ? v : word;
        if (op === '=') { if (!set) this.vars[m[1]] = word; return set ? v : word; }
        if (op === '+') return set ? word : '';
        if (op === '?') { if (!set) throw new Error(`${m[1]}: ${word || 'parameter null or not set'}`); return v; }
      }
      if ((m = /^(\w+)(%%|%|##|#)(.*)$/.exec(body))) {
        const v = this.param(m[1]), re = globRe(this.expandStr(m[3])).source.slice(1, -1).replace(/\[\^\/\]\*/g, '.*').replace(/\[\^\/\]/g, '.');
        if (m[2] === '%') { for (let k = v.length; k >= 0; k--) if (new RegExp('^' + re + '$').test(v.slice(k))) return v.slice(0, k); return v; }
        if (m[2] === '%%') { for (let k = 0; k <= v.length; k++) if (new RegExp('^' + re + '$').test(v.slice(k))) return v.slice(0, k); return v; }
        if (m[2] === '#') { for (let k = 0; k <= v.length; k++) if (new RegExp('^' + re + '$').test(v.slice(0, k))) return v.slice(k); return v; }
        if (m[2] === '##') { for (let k = v.length; k >= 0; k--) if (new RegExp('^' + re + '$').test(v.slice(0, k))) return v.slice(k); return v; }
      }
      if ((m = /^(\w+)\/(\/?)([^/]*)\/?(.*)$/.exec(body))) {
        const v = this.param(m[1]), from = this.expandStr(m[3]), to = this.expandStr(m[4]);
        if (!from) return v;
        return m[2] ? v.split(from).join(to) : v.replace(from, to);
      }
      if ((m = /^(\w+):\s*\(?(-?\d+)\)?(?::(\d+))?$/.exec(body))) { const v = this.param(m[1]); let s = +m[2]; if (s < 0) s = Math.max(0, v.length + s); return m[3] !== undefined ? v.substr(s, +m[3]) : v.slice(s); }
      if ((m = /^(\w+)(\^\^|,,)$/.exec(body))) { const v = this.param(m[1]); return m[2] === '^^' ? v.toUpperCase() : v.toLowerCase(); }
      return this.param(body);
    }
    /* "$*" and "${a[*]}" put the first character of IFS between the items, a space when IFS is unset */
    ifsJoin() { const f = this.vars.IFS; return f === undefined ? ' ' : f.slice(0, 1); }
    /* $VAR, ${...}, $(...), $((...)) inside one piece of text */
    expandStr(s) {
      let out = '', i = 0;
      while (i < s.length) {
        const c = s[i];
        if (c === '\\' && i + 1 < s.length && '"\\$`'.includes(s[i + 1])) { out += s[i + 1]; i += 2; continue; }
        if (c !== '$') { out += c; i++; continue; }
        if (s.startsWith('$((', i)) { const k = this.matchParen(s, i + 1); out += String(this.arith(this.expandStr(s.slice(i + 3, k - 1)))); i = k + 1; continue; }
        if (s[i + 1] === '(') { const k = this.matchParen(s, i + 1); const r = this.capture(s.slice(i + 2, k)); this.substCode = this.last; out += r.replace(/\n+$/, ''); i = k + 1; continue; }
        if (s[i + 1] === '{') { const k = s.indexOf('}', i); out += this.braceParam(s.slice(i + 2, k)); i = k + 1; continue; }
        const m = /^(\w+|[?#@*$!0-9])/.exec(s.slice(i + 1));
        if (!m) { out += '$'; i++; continue; }
        const nm = /^\d/.test(m[1]) ? m[1][0] : m[1];
        out += this.param(nm); i += 1 + nm.length;
      }
      return out;
    }
    capture(src) {
      const save = this.outHook; let buf = '';
      this.outHook = s => { buf += s; }; this.notty = (this.notty || 0) + 1;
      try { this.runSrc(src, true); } finally { this.outHook = save; this.notty--; }
      return buf;
    }
    braces(s) {
      let m = null;
      for (let i = 0; i < s.length; i++) {
        if (s[i] === '$' && s[i + 1] === '{') { const k = s.indexOf('}', i); if (k < 0) break; i = k; continue; }
        if (s[i] !== '{') continue;
        const k = s.indexOf('}', i + 1); if (k < 0) break;
        const body = s.slice(i + 1, k);
        if (body.includes('{') || !(body.includes(',') || /^(-?\d+\.\.-?\d+|[a-z]\.\.[a-z])$/.test(body))) continue;
        m = [s, s.slice(0, i), body, s.slice(k + 1)]; break;
      }
      if (!m) return [s];
      let items;
      const r = /^(-?\d+)\.\.(-?\d+)$/.exec(m[2]) || /^([a-z])\.\.([a-z])$/.exec(m[2]);
      if (r) {
        const num = /\d/.test(r[1]), a = num ? +r[1] : r[1].charCodeAt(0), b = num ? +r[2] : r[2].charCodeAt(0), st = a <= b ? 1 : -1;
        items = []; for (let k = a; st > 0 ? k <= b : k >= b; k += st) items.push(num ? String(k) : String.fromCharCode(k));
      } else if (m[2].includes(',')) items = m[2].split(',');
      else return [s];
      return items.flatMap(x => this.braces(m[1] + x + m[3]));
    }
    /* one word becomes zero or more argument strings */
    expandWord(w) {
      if (w.parts.some(p => p.arr !== undefined)) return [w.parts.map(p => p.t).join('')];
      if (w.parts.length === 1 && w.parts[0].q === 2) {
        const t = w.parts[0].t; let m;
        if (t === '$@' || t === '${@}') return this.args.slice();
        if ((m = /^\$\{(\w+)\[@\]\}$/.exec(t))) return this.arrVals(m[1]);
        if ((m = /^\$\{(\w+\[@\]|@)(\/\/?|##?|%%?|\^\^?|,,?)([^}]*)\}$/.exec(t))) {
          const all = m[1] === '@' ? this.args : this.arrVals(m[1].slice(0, -3)), keep = this.vars.__el;
          try { return all.map(x => { this.vars.__el = x; return this.braceParam('__el' + m[2] + m[3]); }); } finally { if (keep === undefined) delete this.vars.__el; else this.vars.__el = keep; }
        }
        if ((m = /^\$\{(\w+)\[@\]:(-?\d+)(?::(\d+))?\}$/.exec(t))) { const v = this.arrVals(m[1]); let st = +m[2]; if (st < 0) st = Math.max(0, v.length + st); return m[3] !== undefined ? v.slice(st, st + +m[3]) : v.slice(st); }
        if ((m = /^\$\{!(\w+)\[@\]\}$/.exec(t))) return this.arrKeys(m[1]);
      }
      if (w.parts.some(p => p.ps)) return [w.parts.map(p => { if (!p.ps) return p.q === 1 ? p.t : this.expandStr(p.t); const fd = this.psN = (this.psN || 64) - 1; const body = this.capture(p.t); this.psN = fd; if (!this.node('/dev/fd')) this.mk('/dev/fd', 'd', 0o755, 'root'); this.mk('/dev/fd/' + fd, 'f', 0o444, this.user, body); return '/dev/fd/' + fd; }).join('')];
      let anyQ = false, text = '', globbable = '', splitParts = [];
      w.parts.forEach(p => {
        if (p.q === 1) { anyQ = true; text += p.t; globbable += p.t.replace(/[*?[]/g, '\\$&'); splitParts.push([p.t, false]); return; }
        const v = this.expandStr(p.t);
        if (p.q === 2) { anyQ = true; text += v; globbable += v.replace(/[*?[]/g, '\\$&'); splitParts.push([v, false]); return; }
        text += v; globbable += v; splitParts.push([v, /\$/.test(p.t)]);
      });
      const raw = w.parts.map(p => p.t).join('');
      if (!anyQ) {
        let t = raw;
        if (t === '~' || t.startsWith('~/')) t = HOME + t.slice(1);
        const bs = /\{[^{}]*(,|\.\.)[^{}]*\}/.test(t) ? this.braces(t) : [t];
        const out = [];
        bs.forEach(b => {
          const v = this.expandStr(b);
          const pieces = /\$/.test(b) ? this.ifsSplit(v) : [v];
          pieces.forEach(pc => { if (hasGlob(pc)) { const g = this.glob(pc); if (g.length) out.push(...g); else if (!this.shopt('nullglob')) out.push(pc); } else out.push(pc); });
        });
        return out;
      }
      if (hasGlob(globbable.replace(/\\[*?[]/g, ''))) { const g = this.glob(globbable); if (g.length) return g; if (this.shopt('nullglob')) return []; }
      return [text];
    }
    /* word splitting with $IFS: white space runs count as one break, every other IFS character is a break of its own */
    ifsSplit(v) {
      const ifs = this.vars.IFS ?? ' \t\n';
      if (ifs === '') return v === '' ? [] : [v];
      const esc = x => x.replace(/[\\\]^-]/g, '\\$&'), ws = [...ifs].filter(c => ' \t\n'.includes(c)).join(''), nw = [...ifs].filter(c => !' \t\n'.includes(c)).join('');
      if (ws) v = v.replace(new RegExp('^[' + esc(ws) + ']+|[' + esc(ws) + ']+$', 'g'), '');
      if (v === '') return [];
      const re = nw ? new RegExp((ws ? '[' + esc(ws) + ']*' : '') + '[' + esc(nw) + ']' + (ws ? '[' + esc(ws) + ']*|[' + esc(ws) + ']+' : '')) : new RegExp('[' + esc(ws) + ']+');
      const f = v.split(re);
      if (nw && f.length > 1 && f[f.length - 1] === '') f.pop();
      return f;
    }
    glob(pat) {
      const absP = pat.startsWith('/'), parts = pat.split('/').filter(Boolean);
      let paths = [absP ? '/' : ''];
      parts.forEach((part, idx) => {
        const next = [];
        paths.forEach(base => {
          const dir = this.node(base === '' ? this.cwd : this.abs(base));
          if (!hasGlob(part.replace(/\\[*?[]/g, ''))) { const name = part.replace(/\\(.)/g, '$1'); const p = base === '' ? name : base.replace(/\/$/, '') + '/' + name; if (this.node(this.abs(p), false)) next.push(p); return; }
          if (!dir || dir.type !== 'd') return;
          const re = this.shopt('nocaseglob') ? new RegExp(globRe(part).source, 'i') : globRe(part);
          Object.keys(dir.kids).sort().forEach(n => { if (n.startsWith('.') && !part.startsWith('.') && !this.shopt('dotglob')) return; if (re.test(n)) next.push(base === '' ? n : base.replace(/\/$/, '') + '/' + n); });
        });
        paths = next;
        if (idx < parts.length - 1) paths = paths.filter(p => { const n = this.node(this.abs(p)); return n && n.type === 'd'; });
      });
      return paths.filter(Boolean).sort();
    }

    /* ---------- running ---------- */
    out(s) { if (this.outHook) this.outHook(s); else this.buf += s; }
    run(line) {
      this.buf = ''; this.err = false;
      const t = line.trim();
      if (!t) return { out: '', code: this.last };
      let src = t;
      if (/^!!$/.test(t) && this.hist.length) src = this.hist[this.hist.length - 1];
      else if (/^!\d+$/.test(t)) src = this.hist[+t.slice(1) - 1] || t;
      this.hist.push(src);
      if (src !== t) this.out(src + '\n');
      this.runSrc(src);
      this.reap();
      return { out: this.buf, code: this.last };
    }
    runSrc(src, sub) {
      let tree;
      const heres = [];
      /* here documents: lines after the command up to the end word */
      src = src.replace(/(?<!<)<<(-?)\s*(['"]?)(\w+)\2([^\n]*)\n([\s\S]*?)\n\t*\3(\n|$)/g, (all, dash, q, tag, rest, body) => { heres.push({ body: (dash ? body.replace(/^\t+/gm, '') : body) + '\n', quoted: !!q }); return `<<${tag}${rest}\n` + '\n'.repeat(body.split('\n').length + 1); });
      this.heres = heres;
      try { tree = this.parse(this.lex(src)); } catch (e) { this.out(e.eof && this.script ? `${this.script}: line ${src.split('\n').length}: ${e.message}\n` : `bash: ${e.message}\n`); this.last = 2; return; }
      try { this.exec(tree, ''); } catch (e) {
        if (e && e.exit !== undefined) {
          this.last = e.exit; if (sub) throw e;
          if (e.errexit) { this.out('(set -e stopped the commands here because one failed. A real interactive shell would now close, which is why set -e belongs in scripts. It is now switched off again.)\n'); this.opts.errexit = false; }
          return;
        }
        if (e && (e.brk || e.cont)) return;
        this.out(`bash: ${e.message}\n`); this.last = 1;
      }
    }
    exec(node, input) {
      switch (node.t) {
        case 'list': {
          let code = 0;
          for (const it of node.items) {
            this.condFail = false;
            code = it.bg ? this.background(it.p, input) : this.exec(it.p, input);
            if (code && !this.noErr && !this.condFail && !(it.p.t === 'pipe' && it.p.neg)) {
              if (this.traps && this.traps.ERR && !this.inTrap) this.runTrap('ERR');
              if (this.opts && this.opts.errexit) throw { exit: code, errexit: true };
            }
          }
          return code;
        }
        case 'and': { this.noErr = (this.noErr || 0) + 1; let a; try { a = this.exec(node.a, input); } finally { this.noErr--; } if (a !== 0) { this.condFail = true; return a; } return this.exec(node.b, input); }
        case 'or': { this.noErr = (this.noErr || 0) + 1; let a; try { a = this.exec(node.a, input); } finally { this.noErr--; } return a !== 0 ? this.exec(node.b, input) : a; }
        case 'pipe': {
          let data = input, code = 0;
          /* in bash every part of a pipeline with more than one command runs in its own subshell, so a variable set
             there (echo hi | read x) is gone afterwards */
          const keep = node.cmds.length > 1 ? { vars: Object.assign({}, this.vars), cwd: this.cwd } : null;
          const codes = [];
          node.cmds.forEach((c, k) => {
            const last = k === node.cmds.length - 1;
            if (last) { code = this.withRedir(c, data, null); codes.push(code); return; }
            let buf = '';
            const save = this.outHook; this.outHook = s => { buf += s; }; this.notty = (this.notty || 0) + 1;
            try { codes.push(this.withRedir(c, data, null)); } finally { this.outHook = save; this.notty--; }
            data = buf;
          });
          if (keep) { this.vars = keep.vars; this.cwd = keep.cwd; }
          this.arrays = this.arrays || {}; this.arrays.PIPESTATUS = codes.map(String);
          if (this.opts && this.opts.pipefail) { const bad = codes.filter(x => x !== 0); code = bad.length ? bad[bad.length - 1] : 0; }
          if (node.neg) code = code ? 0 : 1;
          this.last = code;
          return code;
        }
        default: return this.withRedir(node, input, null);
      }
    }
    withRedir(node, input, _) {
      const red = node.redir || [];
      if (!red.length) return this.last = this.simple(node, input);
      /* each of stdout (1) and stderr (2) points at the terminal or a file, processed left to right as bash does */
      const target = (f, mode) => {
        if (f === '/dev/null') return { null: true };
        const p = this.abs(f), n = this.node(p);
        if (n && n.type === 'd') throw new Error(`${f}: Is a directory`);
        if (n && mode === '>' && this.opts && this.opts.noclobber) throw new Error(`${f}: cannot overwrite existing file`);
        if (n && !this.can(n, 'w')) throw new Error(`${f}: Permission denied`);
        const dir = this.node(dirName(p));
        if (!dir) throw new Error(`${f}: No such file or directory`);
        if (!n && !this.can(dir, 'w')) throw new Error(`${f}: Permission denied`);
        return { p, app: mode === '>>' || mode === '&>>' };
      };
      const fd = { 1: { tty: 1 }, 2: { tty: 2 } }, opened = [];
      const open = (f, mode) => { const t = target(f, mode); if (t.p) { let n = this.node(t.p); if (!n) n = this.mk(t.p, 'f', 0o666 & ~this.umask, this.user, ''); if (!t.app) { n.data = ''; } n.mtime = this.now(); opened.push(t.p); } return t; };
      try {
        for (const r of red) {
          if (r.op === '<') { const p = this.expandWord(r.w)[0]; const n = this.node(this.abs(p)); if (!n) throw new Error(`${p}: No such file or directory`); if (!this.can(n, 'r')) throw new Error(`${p}: Permission denied`); input = n.data; }
          else if (r.op === '<<') { const h = this.heres.shift() || { body: '', quoted: true }; input = h.quoted ? h.body : this.expandStr(h.body); }
          else if (r.op === '<<<') input = this.expandWord(r.w).join(' ') + '\n';
          else if (r.op === '>' || r.op === '>>' || r.op === '>|') fd[1] = open(this.expandWord(r.w)[0], r.op);
          else if (r.op === '&>' || r.op === '&>>') fd[1] = fd[2] = open(this.expandWord(r.w)[0], r.op === '&>' ? '>' : '>>');
          else if (r.op === '2>' || r.op === '2>>') fd[2] = open(this.expandWord(r.w)[0], r.op === '2>' ? '>' : '>>');
          else if (r.op === '2>&1') fd[2] = fd[1];
          else if (r.op === '>&2') fd[1] = fd[2];
        }
      } catch (e) { this.out(`bash: ${e.message}\n`); return this.last = 1; }
      const save = this.outHook, saveErr = this.errHook, saveBuf = s => { if (save) save(s); else this.buf += s; };
      const send = (t, s) => {
        if (t.null) return;
        if (t.tty === 1) return saveBuf(s);
        if (t.tty === 2) return saveErr ? saveErr(s) : saveBuf(s);
        const n = this.node(t.p); if (n) { n.data += s; n.mtime = this.now(); }
      };
      this.outHook = s => send(fd[1], s);
      this.errHook = s => send(fd[2], s);
      const nt = fd[1].tty !== 1 && !fd[1].null ? 1 : 0; this.notty = (this.notty || 0) + nt;
      let code;
      try { code = this.simple(node, input); } finally { this.outHook = save; this.errHook = saveErr; this.notty -= nt; }
      return this.last = code;
    }
    /* error output goes through errHook so 2> can catch it */
    eout(s) { if (this.errHook) this.errHook(s); else this.out(s); }

    simple(node, input) {
      /* one turn of a loop body. Returns 'break' or 'next', and passes break 2 or continue 2 on to the outer loop */
      const turn = () => {
        try { this.last = this.bodyCode = this.exec(node.body, input); return ''; } catch (e) {
          if (e && e.brk) { if (e.brk > 1) throw { brk: e.brk - 1 }; return 'break'; }
          if (e && e.cont) { if (e.cont > 1) throw { cont: e.cont - 1 }; return 'next'; }
          throw e;
        }
      };
      const cond = c => { this.noErr = (this.noErr || 0) + 1; try { return this.exec(c, input); } finally { this.noErr--; } };
      if (node.t === 'for') {
        const items = node.words === null ? this.args.slice() : node.words.flatMap(w => this.expandWord(w));
        this.last = 0;
        for (const it of items) { this.vars[node.v] = it; if (turn() === 'break') break; }
        return this.last;
      }
      if (node.t === 'cfor') {
        let guard = 0; this.last = 0;
        try {
          if (node.a.trim()) this.arith(node.a);
          while (guard++ < 10000) {
            if (node.b.trim() && this.arith(node.b) === 0) break;
            if (turn() === 'break') break;
            if (node.c.trim()) this.arith(node.c);
          }
        } catch (e) { if (e instanceof Error) { this.eout(`bash: ${e.message}\n`); return 1; } throw e; }
        if (guard >= 10000) this.eout('practice shell: the loop stopped after 10000 turns\n');
        return this.last;
      }
      if (node.t === 'while') {
        let guard = 0; this.last = 0; this.bodyCode = 0;
        const keepCur = this.cur; if (input) this.cur = { s: input, pos: 0 };
        try {
          while (guard++ < 1000) {
            const c = cond(node.cond);
            if (node.until ? c === 0 : c !== 0) break;
            if (turn() === 'break') break;
          }
        } finally { this.cur = keepCur; }
        if (guard >= 1000) this.eout('practice shell: the loop stopped after 1000 turns\n');
        return this.last = this.bodyCode;
      }
      if (node.t === 'if') {
        for (const [c, b] of node.arms) if (cond(c) === 0) return this.exec(b, input);
        return node.els ? this.exec(node.els, input) : 0;
      }
      if (node.t === 'arith') { try { return this.arith(node.e) !== 0 ? 0 : 1; } catch (e) { this.eout(`bash: ${e.message}\n`); return 1; } }
      if (node.t === 'dbl') return this.dbl(node.text);
      if (node.t === 'case') {
        const v = this.expandWord(node.word).join(' ');
        const hit = p => { const re = globRe(p.parts.map(q => q.q === 1 ? q.t : this.expandStr(q.t)).join('')); return (this.shopt('nocasematch') ? new RegExp(re.source, 'i') : re).test(v); };
        let code = 0, run = false;
        for (const [pats, body, fall] of node.arms) {
          if (!run && !pats.some(hit)) continue;
          code = this.exec(body, input);
          if (fall === ';&') { run = true; continue; }
          run = false;
          if (fall !== ';;&') return code;
        }
        return code;
      }
      if (node.t === 'fn') { (this.fns = this.fns || {})[node.name] = node.body; return 0; }
      if (node.t === 'sub') {
        if (node.keep) return this.exec(node.body, input);
        const keep = { cwd: this.cwd, vars: Object.assign({}, this.vars) };
        try { return this.exec(node.body, input); } finally { this.cwd = keep.cwd; this.vars = keep.vars; }
      }
      /* plain command: leading NAME=value words are assignments */
      if (!this.inTrap) { if (node.ln) this.vars.LINENO = String(node.ln + (this.lineBase || 0)); this.bashCmd = node.words.map(x => this.srcText(x)).concat((node.redir || []).map(r => r.w ? `${r.op} ${this.srcText(r.w)}` : r.op === '<<' ? '<<' + r.tag : r.op)).join(' '); }
      const words = node.words.slice();
      const assigns = []; this.substCode = undefined;
      while (words.length && /^[A-Za-z_]\w*(\[[^\]]*\])?(\+?)=/.test(this.wordText(words[0])) && !words[0].parts[0].q) {
        const w = words.shift(), t = this.wordText(w), m = /^([A-Za-z_]\w*)(?:\[([^\]]*)\])?(\+?)=/.exec(t), name = m[1], app = m[3] === '+';
        const arrPart = w.parts.find(p => p.arr !== undefined);
        if (arrPart) { assigns.push({ name, list: this.arrayItems(arrPart.arr, name), app }); continue; }
        const rest = { parts: [] }; let cut = m[0].length;
        w.parts.forEach(p => { if (cut >= p.t.length) { cut -= p.t.length; return; } rest.parts.push({ t: p.t.slice(cut), q: p.q }); cut = 0; });
        let val = rest.parts.length ? rest.parts.map(p => p.q === 1 ? p.t : this.expandStr(p.t)).join('') : '';
        if (!rest.parts.some(p => p.q) && (val === '~' || val.startsWith('~/'))) val = HOME + val.slice(1);
        if (m[2] !== undefined) { assigns.push({ name, idx: m[2], val, app }); continue; }
        if (this.arrays && Array.isArray(this.arrays[name]) && name !== 'PIPESTATUS') { assigns.push({ name, idx: '0', val, app }); continue; }
        assigns.push([name, app ? (this.vars[name] || '') + val : val]);
      }
      this.psN = 64; let args = words.flatMap(w => this.expandWord(w));
      const nm = x => Array.isArray(x) ? x[0] : x.name;
      const ro = assigns.find(x => this.ro && this.ro.has(nm(x)));
      if (ro) { this.eout(`bash: ${nm(ro)}: readonly variable\n`); return 1; }
      if (!args.length) {
        assigns.forEach(x => { if (this.opts && this.opts.xtrace) this.eout(`${this.vars.PS4 !== undefined ? this.expandStr(this.vars.PS4) : '+ '}${nm(x)}=${Array.isArray(x) ? x[1] : x.val !== undefined ? x.val : '(...)'}\n`); if (Array.isArray(x)) this.vars[x[0]] = x[1]; else this.setArr(x); });
        /* an assignment alone gives the status of its last command substitution, or 0 */
        return this.substCode ?? 0;
      }
      const arrs = assigns.filter(x => !Array.isArray(x)); arrs.forEach(x => this.setArr(x));
      assigns.splice(0, assigns.length, ...assigns.filter(x => Array.isArray(x)));
      if (this.aliases[args[0]] && !this.inAlias) {
        const toks = this.lex(this.aliases[args[0]]).filter(t => t.w).map(t => this.wordText(t.w));
        args = toks.concat(args.slice(1));
      }
      const saved = assigns.map(([k]) => [k, this.vars[k]]);
      assigns.forEach(([k, v]) => { this.vars[k] = v; });
      const keepTmp = this.tmpEx; this.tmpEx = new Set([...(keepTmp || []), ...assigns.map(([k]) => k)]);
      try { return this.call(args, input); } finally { this.tmpEx = keepTmp; saved.forEach(([k, v]) => { if (v === undefined) delete this.vars[k]; else this.vars[k] = v; }); }
    }
    call(args, input) {
      let name = args[0];
      if (this.opts && this.opts.xtrace && !this.inTrap) this.eout((this.vars.PS4 !== undefined ? this.expandStr(this.vars.PS4) : '+ ') + args.map(x => /^[\w.\/:=@%+,-]+$/.test(x) ? x : `'${x.replace(/'/g, "'\\''")}'`).join(' ') + '\n');
      if (this.fns && this.fns[name]) {
        const keep = this.args; this.args = args.slice(1);
        const stack = this.fnStack = this.fnStack || [];
        if (stack.length >= 150) throw new Error(`${name}: maximum function nesting level exceeded (150, the practice shell limit)`);
        stack.push(name); (this.arrays = this.arrays || {}).FUNCNAME = stack.slice().reverse();
        (this.frames = this.frames || []).push([]); const keepFn = this.fnName; this.fnName = name;
        try { return this.exec(this.fns[name], input); } catch (e) { if (e && e.ret !== undefined) return e.ret; throw e; } finally {
          this.args = keep; this.fnName = keepFn;
          stack.pop(); if (stack.length) this.arrays.FUNCNAME = stack.slice().reverse(); else delete this.arrays.FUNCNAME;
          this.frames.pop().reverse().forEach(([k, had, v, hadA, va, wasAssoc]) => {
            if (had) this.vars[k] = v; else delete this.vars[k];
            this.arrays = this.arrays || {}; if (hadA) this.arrays[k] = va; else delete this.arrays[k];
            this.assoc = this.assoc || new Set(); if (wasAssoc) this.assoc.add(k); else this.assoc.delete(k);
          });
        }
      }
      if (name.includes('/')) return this.runFile(name, args.slice(1), input, true);
      if (!BUILTIN.has(name) && !(this.fns && this.fns[name])) {
        const hit = this.lookup(name);
        if (hit && !/^#!practice /.test(hit.n.data)) return this.runFile(hit.path, args.slice(1), input, true);
        if (!hit && CMDS.includes(name)) { this.eout(`${name}: command not found\n`); return 127; }
      }
      const f = C[name];
      if (!f) { this.eout(`${name}: command not found\n`); return 127; }
      const keepErr = this.err; this.err = false;
      try { return f.call(this, args.slice(1), input, name) || 0; } catch (e) {
        if (e && (e.exit !== undefined || e.ret !== undefined || e.brk || e.cont)) throw e;
        this.eout(`${name}: ${e.message}\n`); return 1;
      } finally { this.err = this.err || keepErr; }
    }
    runFile(path, args, input, needX, fresh) {
      const isNew = needX || fresh;
      const p = this.abs(path), n = this.node(p);
      if (!n) { this.eout(`bash: ${path}: No such file or directory\n`); return 127; }
      if (n.type === 'd') { this.eout(`bash: ${path}: Is a directory\n`); return 126; }
      if (needX && !this.can(n, 'x')) { this.eout(`bash: ${path}: Permission denied\n`); return 126; }
      if (!this.can(n, 'r')) { this.eout(`bash: ${path}: Permission denied\n`); return 126; }
      if (/^#!practice /.test(n.data)) return this.call([n.data.slice(10).trim()].concat(args), input);
      const keep = { args: this.args, script: this.script, vars: Object.assign({}, this.vars), exported: new Set(this.exported) };
      this.args = args; this.script = path;
      if (isNew) this.vars = this.childVars();
      const keepTraps = this.traps, keepOpts = Object.assign({}, this.opts || {}), keepFrames = this.frames;
      if (isNew) { this.traps = {}; this.opts = { noclobber: keepOpts.noclobber }; this.frames = []; }
      let death = '';
      try { this.runSrc(n.data, true); } catch (e) { if (e && e.exit !== undefined) { this.last = e.exit; if (e.sig && e.sig !== 2 && DEATH[e.sig]) death = DEATH[e.sig]; } else throw e; } finally {
        if (isNew) { if (this.traps.EXIT) { const st = this.last; this.runTrap('EXIT'); this.last = st; } this.traps = keepTraps; this.opts = keepOpts; this.frames = keepFrames; }
        this.args = keep.args; this.script = keep.script;
        if (isNew) { this.vars = keep.vars; this.exported = keep.exported; }   /* ./script runs in a new shell, so its variables vanish. source keeps them */
      }
      if (death) this.eout(death + '\n');   /* the parent shell reports how its child died */
      return this.last;
    }
    /* the variables a child process sees: only exported ones (and NAME=value given just for this command) */
    childVars() { const v = {}; Object.keys(this.vars).forEach(k => { if (this.exported.has(k) || (this.tmpEx && this.tmpEx.has(k))) v[k] = this.vars[k]; }); ['PWD', 'HOME', 'PATH'].forEach(k => { if (k in this.vars && !(k in v) && this.exported.has(k)) v[k] = this.vars[k]; }); return v; }
    /* search the folders in PATH for an executable file, the way bash does */
    lookup(name) {
      for (const d of (this.vars.PATH ?? '/usr/local/bin:/usr/bin:/bin').split(':')) {
        const path = norm((d === '' ? this.cwd : this.abs(d)) + '/' + name), n = this.node(path);
        if (n && n.type === 'f' && (n.mode & 0o111)) return { path, n };
      }
      return null;
    }
    /* read the files named in args, or the input when there are none */
    inputs(args, input, cmd) {
      if (!args.length || (args.length === 1 && args[0] === '-')) return [{ name: '-', data: input }];
      return args.map(a => {
        const n = this.node(this.abs(a));
        if (!n) { this.eout(`${cmd}: ${a}: No such file or directory\n`); this.err = true; return null; }
        if (n.type === 'd') { this.eout(`${cmd}: ${a}: Is a directory\n`); this.err = true; return null; }
        if (!this.can(n, 'r')) { this.eout(`${cmd}: ${a}: Permission denied\n`); this.err = true; return null; }
        return { name: a, data: n.data };
      }).filter(Boolean);
    }
    removeNode(p) { const d = this.node(dirName(p)); delete d.kids[baseName(p)]; d.mtime = this.now(); }
  }

  /* split options: returns [flags set, rest]. 'n:' style values are read from the next word */
  function opts(args, withVal = '') {
    const f = {}, rest = [];
    for (let i = 0; i < args.length; i++) {
      const a = args[i];
      if (a === '--') { rest.push(...args.slice(i + 1)); break; }
      if (/^--[\w-]+(=.*)?$/.test(a)) { const [k, v] = a.slice(2).split('='); f['--' + k] = v ?? true; continue; }
      if (/^-[A-Za-z0-9]/.test(a) && !/^-\d+$/.test(a) && (withVal.includes(a[1]) || /^-[A-Za-z0-9]+$/.test(a))) {
        for (let j = 1; j < a.length; j++) {
          const ch = a[j];
          if (withVal.includes(ch)) { f[ch] = a.slice(j + 1) || args[++i]; break; }
          f[ch] = true;
        }
        continue;
      }
      rest.push(a);
    }
    return [f, rest];
  }

  /* ---------- the commands ---------- */
  const MAN = {
    ls: 'ls [OPTION]... [FILE]...  list folder contents. -l long listing, -a show hidden files, -A all but . and .., -h human sizes, -R recursive, -d the folder itself, -1 one per line, -t newest first, -S biggest first, -r reverse.',
    cd: 'cd [DIR]  change the current folder. cd alone goes home, cd - goes back, cd .. goes up one level.',
    pwd: 'pwd  print the full path of the current folder.',
    mkdir: 'mkdir [-p] DIR...  make folders. -p makes parent folders too and does not complain if they exist.',
    touch: 'touch FILE...  make an empty file, or update the time of a file that exists.',
    cp: 'cp [-r] [-i] SOURCE... DEST  copy files. -r copies folders and everything inside.',
    mv: 'mv SOURCE... DEST  move or rename files and folders.',
    rm: 'rm [-r] [-f] [-i] FILE...  remove files. -r removes folders and their contents, -f never asks and ignores missing files. There is no recycle bin.',
    rmdir: 'rmdir DIR...  remove empty folders.',
    cat: 'cat [-n] [FILE]...  print files one after another. -n numbers the lines.',
    echo: 'echo [-n] [-e] [TEXT]...  print text. -n no newline at the end, -e understand backslash escapes such as \\n and \\t.',
    head: 'head [-n N] [FILE]...  print the first 10 lines, or N lines.',
    tail: 'tail [-n N] [FILE]...  print the last 10 lines, or N lines. -n +N starts at line N.',
    wc: 'wc [-l] [-w] [-c] [FILE]...  count lines, words and bytes.',
    grep: 'grep [-i] [-v] [-n] [-c] [-o] [-r] [-E] [-w] [-l] PATTERN [FILE]...  print lines that match a pattern. -i ignore case, -v lines that do not match, -n line numbers, -c count, -r search folders, -E extended regular expressions.',
    sort: 'sort [-r] [-n] [-u] [-t SEP] [-k N] [FILE]...  sort lines. -n by number, -r reverse, -u drop repeats, -t field separator, -k sort on field N.',
    uniq: 'uniq [-c] [-d] [-u] [FILE]  drop repeated lines that are next to each other. -c count them. Sort first to group repeats.',
    cut: 'cut -d SEP -f LIST | -c LIST [FILE]...  print selected fields or characters of each line.',
    tr: 'tr [-d] [-s] SET1 [SET2]  translate or delete characters read from standard input.',
    sed: 'sed [-n] [-i] [-e SCRIPT] SCRIPT [FILE]...  stream editor. s/old/new/g replaces, Np prints line N, /re/d deletes matching lines.',
    awk: 'awk [-F SEP] \'PROGRAM\' [FILE]...  pattern scanning language. $1 is the first field, NF the number of fields, NR the line number.',
    chmod: 'chmod MODE FILE...  change permission bits. MODE is octal like 755 or symbolic like u+x, go-w, a=r.',
    chown: 'chown OWNER[:GROUP] FILE...  change the owner. Only root can give files away, so use sudo.',
    find: 'find [PATH] [-name GLOB] [-iname GLOB] [-type f|d|l] [-size +N[kMc]] [-maxdepth N] [-empty] [-newer FILE] [-exec CMD {} ;]  search for files under a folder.',
    ln: 'ln [-s] TARGET LINK  make a hard link, or a symbolic link with -s.',
    man: 'man COMMAND  show the manual page of a command. Here it shows a short summary.',
    history: 'history  list the commands you typed. !N runs command N again, !! runs the last one.',
    sudo: 'sudo COMMAND  run one command as root. In this practice shell no password is asked.',
    ps: 'ps [aux]  list processes.',
    kill: 'kill [-SIGNAL] PID  send a signal to a process. The default is TERM (15).',
    tar: 'tar -c|-x|-t [-v] [-z|-J|-j] -f ARCHIVE [-C DIR] [FILE]...  bundle files into one archive. -c create, -x extract, -t list, -f the archive file, -z gzip, -J xz, -j bzip2, -C work inside DIR.',
    gzip: 'gzip [-d] [-k] [-c] [-l] [-r] FILE...  compress files to FILE.gz. -d decompress, -k keep the original, -c write to standard output, -l show sizes.',
    xz: 'xz [-d] [-k] [-c] FILE...  compress files to FILE.xz, smaller than gzip but slower.',
    bzip2: 'bzip2 [-d] [-k] [-c] FILE...  compress files to FILE.bz2.',
    zip: 'zip [-r] [-q] ARCHIVE.zip FILE...  make a zip archive. -r includes folders and everything inside.',
    unzip: 'unzip [-l] [-o] [-q] ARCHIVE.zip [-d DIR]  extract a zip archive. -l lists it, -d extracts into DIR, -o overwrites without asking.'
  };
  const C = {};
  C.pwd = function () { this.out(this.cwd + '\n'); };
  C.cd = function (a) {
    let t = a[0];
    if (!t || t === '~') t = HOME;
    if (t === '-') { t = this.oldpwd; this.out(t + '\n'); }
    const p = this.abs(t), n = this.node(p);
    if (!n) { this.eout(`bash: cd: ${a[0]}: No such file or directory\n`); return 1; }
    if (n.type !== 'd') { this.eout(`bash: cd: ${a[0]}: Not a directory\n`); return 1; }
    if (!this.can(n, 'x')) { this.eout(`bash: cd: ${a[0]}: Permission denied\n`); return 1; }
    this.oldpwd = this.cwd; this.cwd = p; this.vars.OLDPWD = this.oldpwd; this.vars.PWD = p;
  };
  C.ls = function (a) {
    const [f, rest] = opts(a);
    const long = f.l, all = f.a, almost = f.A, hum = f.h || f['--human-readable'];
    const targets = rest.length ? rest : ['.'];
    const nlink = n => n.type === 'd' ? Object.keys(n.kids).filter(k => n.kids[k].type === 'd').length + 2 : 1;
    const sz = n => String(hum ? human(this.size(n)) : this.size(n));
    let W = [1, 1, 1, 1];
    const widths = rows => { W = [0, 0, 0, 0]; rows.forEach(([n]) => { W = [Math.max(W[0], String(nlink(n)).length), Math.max(W[1], n.owner.length), Math.max(W[2], n.group.length), Math.max(W[3], sz(n).length)]; }); };
    const show = (n, name) => {
      if (!long) return name;
      const tgt = n.type === 'l' ? ' -> ' + n.target : '';
      return `${modeStr(n)} ${pad(nlink(n), W[0])} ${pad(n.owner, W[1], true)} ${pad(n.group, W[2], true)} ${pad(sz(n), W[3])} ${when(n.mtime)} ${name}${tgt}`;
    };
    const listing = (n, path) => {
      if (!this.can(n, 'r')) { this.eout(`ls: cannot open directory '${path}': Permission denied\n`); this.err = true; return []; }
      let names = Object.keys(n.kids).filter(k => all || almost || !k.startsWith('.')).sort((x, y) => x.replace(/^\./, '').localeCompare(y.replace(/^\./, ''), 'en', { sensitivity: 'base' }));
      if (f.t) names.sort((x, y) => n.kids[y].mtime - n.kids[x].mtime);
      if (f.S) names.sort((x, y) => this.size(n.kids[y]) - this.size(n.kids[x]));
      if (f.r) names.reverse();
      const rows = names.map(k => [n.kids[k], k]);
      if (all) rows.unshift([n, '.'], [this.node(dirName(this.abs(path))) || n, '..']);
      return rows;
    };
    const files = [], dirs = [];
    targets.forEach(t => {
      const p = this.abs(t), n0 = this.node(p, false);
      if (!n0) { this.eout(`ls: cannot access '${t}': No such file or directory\n`); this.err = true; return; }
      const n = n0.type === 'l' && !long ? this.node(p) || n0 : n0.type === 'l' && t.endsWith('/') ? this.node(p) : n0;
      if (n.type === 'd' && !f.d) dirs.push([n, t]); else files.push([n, t]);
    });
    const parts = [];
    if (files.length) { widths(files); parts.push(files.map(([n, t]) => show(n, t)).join(long || f['1'] || this.notty ? '\n' : '  ')); }
    const walk = (n, t, head) => {
      const rows = listing(n, t);
      let s = head ? `${t}:\n` : '';
      if (long) s += `total ${rows.reduce((sum, [m]) => sum + (m.type === 'd' ? 4 : this.size(m) ? Math.ceil(this.size(m) / 4096) * 4 : 0), 0)}\n`;
      widths(rows);
      s += rows.map(([m, k]) => show(m, k)).join(long || f['1'] || this.notty ? '\n' : '  ');
      parts.push(s.replace(/\n$/, ''));
      if (f.R) rows.filter(([m, k]) => m.type === 'd' && k !== '.' && k !== '..').forEach(([m, k]) => walk(m, (t === '.' && !head ? '.' : t).replace(/\/$/, '') + '/' + k, true));
    };
    dirs.forEach(([n, t]) => walk(n, t, targets.length > 1 || f.R));
    const text = parts.filter(x => x !== '').join('\n\n');
    if (text) this.out(text + '\n');
    return this.err ? 2 : 0;
  };
  C.mkdir = function (a) {
    const [f, rest] = opts(a, 'm');
    if (!rest.length) { this.eout('mkdir: missing operand\n'); return 1; }
    let code = 0;
    rest.forEach(t => {
      const p = this.abs(t);
      if (this.node(p, false)) { if (!f.p) { this.eout(`mkdir: cannot create directory '${t}': File exists\n`); code = 1; } return; }
      const parent = this.node(dirName(p));
      if (!parent) { if (f.p) { this.mkdirs(p); if (f.v) this.out(`mkdir: created directory '${t}'\n`); return; } this.eout(`mkdir: cannot create directory '${t}': No such file or directory\n`); code = 1; return; }
      if (!this.can(parent, 'w')) { this.eout(`mkdir: cannot create directory '${t}': Permission denied\n`); code = 1; return; }
      const n = this.mk(p, 'd', f.m ? parseInt(f.m, 8) : 0o777 & ~this.umask, this.user); n.mtime = this.now();
      if (f.v) this.out(`mkdir: created directory '${t}'\n`);
    });
    return code;
  };
  C.rmdir = function (a) {
    let code = 0;
    a.forEach(t => {
      const p = this.abs(t), n = this.node(p, false);
      if (!n) { this.eout(`rmdir: failed to remove '${t}': No such file or directory\n`); code = 1; return; }
      if (n.type !== 'd') { this.eout(`rmdir: failed to remove '${t}': Not a directory\n`); code = 1; return; }
      if (Object.keys(n.kids).length) { this.eout(`rmdir: failed to remove '${t}': Directory not empty\n`); code = 1; return; }
      this.removeNode(p);
    });
    return code;
  };
  C.touch = function (a) {
    if (!a.length) { this.eout('touch: missing file operand\n'); return 1; }
    let code = 0;
    a.filter(x => !x.startsWith('-')).forEach(t => {
      const p = this.abs(t), n = this.node(p);
      if (n) { if (!this.can(n, 'w') && n.owner !== this.user) { this.eout(`touch: cannot touch '${t}': Permission denied\n`); code = 1; return; } n.mtime = this.now(); return; }
      const parent = this.node(dirName(p));
      if (!parent) { this.eout(`touch: cannot touch '${t}': No such file or directory\n`); code = 1; return; }
      if (!this.can(parent, 'w')) { this.eout(`touch: cannot touch '${t}': Permission denied\n`); code = 1; return; }
      this.mk(p, 'f', 0o666 & ~this.umask, this.user, '').mtime = this.now();
    });
    return code;
  };
  const clone = n => { const c = Object.assign({}, n); if (n.kids) { c.kids = {}; Object.entries(n.kids).forEach(([k, v]) => { c.kids[k] = clone(v); }); } return c; };
  C.cp = function (a) {
    const [f, rest] = opts(a);
    if (rest.length < 2) { this.eout(`cp: missing destination file operand after '${rest[0] || ''}'\n`); return 1; }
    const dest = rest.pop(), dp = this.abs(dest), dn = this.node(dp);
    if (rest.length > 1 && (!dn || dn.type !== 'd')) { this.eout(`cp: target '${dest}' is not a directory\n`); return 1; }
    let code = 0;
    rest.forEach(s => {
      const sp = this.abs(s), sn = this.node(sp);
      if (!sn) { this.eout(`cp: cannot stat '${s}': No such file or directory\n`); code = 1; return; }
      if (sn.type === 'd' && !(f.r || f.R || f.a)) { this.eout(`cp: -r not specified; omitting directory '${s}'\n`); code = 1; return; }
      if (!this.can(sn, 'r')) { this.eout(`cp: cannot open '${s}' for reading: Permission denied\n`); code = 1; return; }
      const to = dn && dn.type === 'd' ? dp + '/' + baseName(sp) : dp;
      if (to === sp || to.startsWith(sp + '/')) { this.eout(`cp: cannot copy '${s}' into itself\n`); code = 1; return; }
      const parent = this.node(dirName(to));
      if (!parent) { this.eout(`cp: cannot create regular file '${dest}': No such file or directory\n`); code = 1; return; }
      if (!this.can(parent, 'w')) { this.eout(`cp: cannot create regular file '${to}': Permission denied\n`); code = 1; return; }
      const c = clone(sn); c.name = baseName(to); c.owner = c.group = this.user; c.mtime = f.p || f.a ? sn.mtime : this.now();
      if (!f.p && !f.a) c.mode = sn.mode & ~this.umask & 0o777;
      parent.kids[c.name] = c;
      if (f.v) this.out(`'${s}' -> '${this.tilde(to).replace(/^~/, HOME) === to ? to : to}'\n`);
    });
    return code;
  };
  C.mv = function (a) {
    const [f, rest] = opts(a);
    if (rest.length < 2) { this.eout(`mv: missing destination file operand after '${rest[0] || ''}'\n`); return 1; }
    const dest = rest.pop(), dp = this.abs(dest), dn = this.node(dp);
    if (rest.length > 1 && (!dn || dn.type !== 'd')) { this.eout(`mv: target '${dest}' is not a directory\n`); return 1; }
    let code = 0;
    rest.forEach(s => {
      const sp = this.abs(s), sn = this.node(sp, false);
      if (!sn) { this.eout(`mv: cannot stat '${s}': No such file or directory\n`); code = 1; return; }
      const to = dn && dn.type === 'd' ? dp + '/' + baseName(sp) : dp;
      if (to.startsWith(sp + '/')) { this.eout(`mv: cannot move '${s}' to a subdirectory of itself\n`); code = 1; return; }
      const from = this.node(dirName(sp)), parent = this.node(dirName(to));
      if (!parent) { this.eout(`mv: cannot move '${s}' to '${dest}': No such file or directory\n`); code = 1; return; }
      if (!this.can(from, 'w') || !this.can(parent, 'w')) { this.eout(`mv: cannot move '${s}' to '${dest}': Permission denied\n`); code = 1; return; }
      if (f.n && parent.kids[baseName(to)]) return;
      delete from.kids[sn.name]; sn.name = baseName(to); parent.kids[sn.name] = sn; from.mtime = parent.mtime = this.now();
      if (f.v) this.out(`renamed '${s}' -> '${dest}'\n`);
    });
    return code;
  };
  C.rm = function (a) {
    const [f, rest] = opts(a);
    if (!rest.length) { if (!f.f) { this.eout('rm: missing operand\n'); return 1; } return 0; }
    let code = 0;
    rest.forEach(t => {
      const p = this.abs(t), n = this.node(p, false);
      if (p === '/' ) { this.eout("rm: it is dangerous to operate recursively on '/'\nrm: use --no-preserve-root to override this failsafe\n"); code = 1; return; }
      if (!n) { if (!f.f) { this.eout(`rm: cannot remove '${t}': No such file or directory\n`); code = 1; } return; }
      if (n.type === 'd' && !(f.r || f.R || f['--recursive'])) { this.eout(`rm: cannot remove '${t}': Is a directory\n`); code = 1; return; }
      if (!this.can(this.node(dirName(p)), 'w')) { this.eout(`rm: cannot remove '${t}': Permission denied\n`); code = 1; return; }
      const parent = this.node(dirName(p));
      if ((parent.mode & 0o1000) && n.owner !== this.user && parent.owner !== this.user && this.user !== 'root') { this.eout(`rm: cannot remove '${t}': Operation not permitted\n`); code = 1; return; }
      this.removeNode(p);
      if (f.v) this.out(`removed '${t}'\n`);
    });
    return code;
  };
  C.cat = function (a, input) {
    const [f, rest] = opts(a);
    let n = 0;
    this.inputs(rest, input, 'cat').forEach(x => {
      if (f.n) this.out(join(lines(x.data).map(l => pad(++n, 6) + '\t' + l)));
      else this.out(x.data);
    });
    return this.err ? 1 : 0;
  };
  C.tac = function (a, input) { this.inputs(a, input, 'tac').forEach(x => this.out(join(lines(x.data).reverse()))); };
  C.rev = function (a, input) { this.inputs(a, input, 'rev').forEach(x => this.out(join(lines(x.data).map(l => [...l].reverse().join(''))))); };
  C.nl = function (a, input) { let n = 0; this.inputs(a, input, 'nl').forEach(x => this.out(join(lines(x.data).map(l => l === '' ? '' : pad(++n, 6) + '\t' + l)))); };
  C.less = C.more = function (a, input) { this.out('(the practice shell prints the whole file. In a real terminal less shows one screen at a time: Space next page, b back, /word search, q quit)\n'); return C.cat.call(this, a, input); };
  const unesc = s => s.replace(/\\(n|t|\\|a|e|0\d*)/g, (_, c) => ({ n: '\n', t: '\t', '\\': '\\', a: '', e: '' }[c] ?? ''));
  C.echo = function (a) {
    let i = 0, nl = true, e = false;
    while (a[i] && /^-[neE]+$/.test(a[i])) { if (a[i].includes('n')) nl = false; if (a[i].includes('e')) e = true; i++; }
    let s = a.slice(i).join(' ');
    if (e) { const k = s.indexOf('\\c'); if (k >= 0) { s = s.slice(0, k); nl = false; } s = unesc(s); }
    this.out(s + (nl ? '\n' : ''));
  };
  C.printf = function (a) {
    if (a[0] === '-v') { const name = a[1]; let buf = ''; const save = this.outHook; this.outHook = s => { buf += s; }; let code; try { code = C.printf.call(this, a.slice(2)); } finally { this.outHook = save; } this.vars[name] = buf; return code; }
    if (!a.length) { this.eout('printf: usage: printf format [arguments]\n'); return 2; }
    const fmt = unesc(a[0]); let args = a.slice(1), out = '', code = 0;
    const toNum = v => { v = v === undefined ? '' : String(v); if (/^['"]./.test(v)) return v.codePointAt(1); const t = v.trim(); if (t === '') return 0; if (/^[-+]?(0[xX][0-9a-fA-F]+|\d+(\.\d*)?([eE][-+]?\d+)?|\.\d+)$/.test(t)) return /^[-+]?0[xX]/.test(t) ? parseInt(t, 16) : /^[-+]?0\d+$/.test(t) ? parseInt(t, 8) : +t; this.eout(`bash: printf: ${v}: invalid number\n`); code = 1; return parseFloat(t) || 0; };
    const SPEC = /%([-+ #0]*)(\*|\d+)?(?:\.(\*|\d+))?([diouxXeEfFgGcsbq%])/g;
    do {
      let used = 0;
      out += fmt.replace(SPEC, (all, fl, w, pr, ty) => {
        if (ty === '%') return '%';
        if (w === '*') { w = String(Math.trunc(toNum(args[used++]))); } if (pr === '*') { pr = String(Math.trunc(toNum(args[used++]))); }
        const v = args[used++];
        const spec = '%' + fl + (w || '') + (pr !== undefined ? '.' + pr : '');
        if (ty === 'b') return awkSprintf(spec + 's', [unesc(v ?? '')], toNum, String);
        if (ty === 'q') { const x = v ?? ''; return awkSprintf(spec + 's', [/^[\w.\/@%+=:,-]+$/.test(x) ? x : x === '' ? "''" : x.replace(/([^\w.\/@%+=:,-])/g, '\\$1')], toNum, String); }
        if ('diouxXc'.includes(ty) && ty !== 'c') return awkSprintf(spec + ty, [Math.trunc(toNum(v))], n => n, String);
        if ('eEfFgG'.includes(ty)) return awkSprintf(spec + ty, [toNum(v)], n => n, String);
        if (ty === 'c') return awkSprintf(spec + 's', [(v ?? '').slice(0, 1)], toNum, String);
        return awkSprintf(spec + 's', [v ?? ''], toNum, String);
      });
      args = args.slice(used);
      if (!used) break;
    } while (args.length);
    this.out(out);
    return code;
  };
  function numArg(f, key, def) { const v = f[key]; return v === undefined ? def : String(v); }
  function headTailArgs(a) {
    const b = a.map(x => /^-\d+$/.test(x) ? '-n' + x.slice(1) : x);
    return opts(b, 'nc');
  }
  C.head = function (a, input) {
    const [f, rest] = headTailArgs(a), n = +numArg(f, 'n', 10);
    const xs = this.inputs(rest, input, 'head');
    xs.forEach((x, k) => {
      if (xs.length > 1) this.out(`${k ? '\n' : ''}==> ${x.name} <==\n`);
      if (f.c) { this.out(x.data.slice(0, +f.c)); return; }
      const L = lines(x.data);
      this.out(join(n < 0 ? L.slice(0, n) : L.slice(0, n)));
    });
    return this.err ? 1 : 0;
  };
  C.tail = function (a, input) {
    const [f, rest] = headTailArgs(a), nv = numArg(f, 'n', '10');
    const xs = this.inputs(rest, input, 'tail');
    xs.forEach((x, k) => {
      if (xs.length > 1) this.out(`${k ? '\n' : ''}==> ${x.name} <==\n`);
      const L = lines(x.data);
      this.out(join(nv.startsWith('+') ? L.slice(+nv.slice(1) - 1) : L.slice(Math.max(0, L.length - +nv))));
    });
    if (f.f) this.out('(tail -f keeps waiting for new lines in a real terminal. Press Ctrl C to stop it there)\n');
    return this.err ? 1 : 0;
  };
  C.wc = function (a, input) {
    const [f, rest] = opts(a);
    const pick = f.l || f.w || f.c || f.m ? [f.l, f.w, f.c || f.m] : [true, true, true];
    const xs = this.inputs(rest, input, 'wc'), tot = [0, 0, 0];
    const rows = xs.map(x => { const v = [(x.data.match(/\n/g) || []).length, x.data.split(/\s+/).filter(Boolean).length, f.m ? [...x.data].length : enc(x.data)]; v.forEach((y, i) => { tot[i] += y; }); return [v, x.name]; });
    if (xs.length > 1) rows.push([tot, 'total']);
    const one = pick.filter(Boolean).length === 1 && xs.length === 1;
    const width = one ? 1 : xs.some(x => x.name === '-') ? 7 : Math.max(1, String(tot[2]).length);
    rows.forEach(([v, name]) => { const cols = v.filter((_, i) => pick[i]).map(y => pad(y, width)); this.out(cols.join(' ') + (name !== '-' ? ' ' + name : '') + '\n'); });
    return this.err ? 1 : 0;
  };
  /* POSIX basic and extended regular expressions turned into JavaScript ones (the common parts) */
  function toRe(p, ere, flags) {
    let s = p;
    if (!ere) {
      /* in a basic expression \( \) \{ \} \| \+ \? are the special ones and the bare characters are plain */
      let o = '', inSet = false;
      for (let i = 0; i < s.length; i++) {
        const c = s[i];
        if (inSet) { o += c; if (c === ']' ) inSet = false; continue; }
        if (c === '[') { inSet = true; o += c; if (s[i + 1] === '^') o += s[++i]; if (s[i + 1] === ']') o += s[++i]; continue; }
        if (c === '\\' && '(){}|+?'.includes(s[i + 1])) { o += s[++i]; continue; }
        if ('(){}|+?'.includes(c)) { o += '\\' + c; continue; }
        if (c === '\\') { o += c + (s[++i] || ''); continue; }
        o += c;
      }
      s = o;
    }
    s = s.replace(/\[\[:(\w+):\]\]/g, (_, c) => ({ alpha: '[A-Za-z]', digit: '[0-9]', alnum: '[A-Za-z0-9]', upper: '[A-Z]', lower: '[a-z]', space: '\\s', punct: '[!-/:-@[-`{-~]' }[c] || '.'))
      .replace(/\[:(\w+):\]/g, (_, c) => ({ alpha: 'A-Za-z', digit: '0-9', alnum: 'A-Za-z0-9', upper: 'A-Z', lower: 'a-z', space: '\\s', punct: '!-/:-@[-`{-~' }[c] || ''));
    s = s.replace(/\\</g, '\\b').replace(/\\>/g, '\\b');
    return new RegExp(s, flags);
  }
  C.grep = function (a, input, nm) {
    const pats = [], a2 = [];
    for (let i = 0; i < a.length; i++) { if (a[i] === '-e') pats.push(a[++i] ?? ''); else if (/^-e./.test(a[i])) pats.push(a[i].slice(2)); else a2.push(a[i]); }
    const [f, rest] = opts(a2, 'ABCm');
    if (nm === 'egrep') f.E = true;
    if (!pats.length) { if (!rest.length) { this.eout('Usage: grep [OPTION]... PATTERNS [FILE]...\n'); return 2; } pats.push(rest.shift()); }
    const after = +(f.A ?? f.C ?? 0), before = +(f.B ?? f.C ?? 0), maxm = f.m !== undefined ? +f.m : Infinity;
    let re;
    try {
      const one = pat => f.F ? pat.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') : toRe(pat, f.E || f.P, '').source;
      re = new RegExp(pats.map(x => '(?:' + one(x) + ')').join('|'), f.i ? 'i' : '');
      if (f.w) re = new RegExp('(?<![A-Za-z0-9_])(?:' + re.source + ')(?![A-Za-z0-9_])', re.flags);
      if (f.x) re = new RegExp('^(?:' + re.source + ')$', re.flags);
    } catch (e) { this.eout(`grep: invalid regular expression\n`); return 2; }
    let files = rest;
    if ((f.r || f.R) && !files.length) files = ['.'];
    if (f.r || f.R) {
      const out = [];
      files.forEach(t => {
        const walk = (p, shown) => { const n = this.node(this.abs(p)); if (!n) { this.eout(`grep: ${p}: No such file or directory\n`); return; } if (n.type === 'd') { if (!this.can(n, 'r')) { this.eout(`grep: ${p}: Permission denied\n`); return; } Object.keys(n.kids).sort().forEach(k => walk((shown === '.' ? '' : shown.replace(/\/$/, '') + '/') + k, (shown === '.' ? '' : shown.replace(/\/$/, '') + '/') + k)); } else if (n.type === 'f') out.push(shown); };
        walk(t, t);
      });
      files = out;
    }
    const xs = this.inputs(files, input, 'grep');
    const multi = xs.length > 1 || f.r || f.R;
    let any = false;
    xs.forEach(x => {
      let cnt = 0, lastShown = -1, afterLeft = 0;
      const L = lines(x.data), ctx = (after || before) && !f.o && !f.c && !f.l && !f.q;
      const show = (i, sep) => { const pre = (multi && !f.h ? x.name + sep : '') + (f.n ? (i + 1) + sep : ''); this.out(pre + L[i] + '\n'); lastShown = i; };
      for (let i = 0; i < L.length; i++) {
        const l = L[i];
        const m = cnt < maxm && re.test(l) !== !!f.v;
        if (!m) { if (ctx && afterLeft > 0) { show(i, '-'); afterLeft--; } continue; }
        any = true; cnt++;
        if (f.c || f.l || f.q) continue;
        if (ctx) {
          const from = Math.max(0, i - before, lastShown + 1);
          if (lastShown >= 0 && from > lastShown + 1) this.out('--\n');
          for (let k = from; k < i; k++) show(k, '-');
          show(i, ':'); afterLeft = after; continue;
        }
        const pre = (multi && !f.h ? x.name + ':' : '') + (f.n ? (i + 1) + ':' : '');
        if (f.o && !f.v) { const g = new RegExp(re.source, re.flags + 'g'); (l.match(g) || []).forEach(mm => this.out(pre + mm + '\n')); }
        else this.out(pre + l + '\n');
      }
      if (f.c) this.out((multi ? x.name + ':' : '') + cnt + '\n');
      if (f.l && cnt) this.out(x.name + '\n');
    });
    return this.err ? 2 : any ? 0 : 1;
  };
  C.egrep = C.grep;
  C.sort = function (a, input) {
    const [f, rest] = opts(a, 'tko');
    if (f.k) { const km = /^(\d+)(?:,(\d+))?([a-z]*)$/.exec(String(f.k)); if (km) { if (km[3].includes('n')) f.n = true; if (km[3].includes('r')) f.r = true; f.k = km[1] + (km[2] ? ',' + km[2] : ''); } }
    let L = this.inputs(rest, input, 'sort').flatMap(x => lines(x.data));
    const key = l => { if (!f.k) return l; const k = parseInt(f.k, 10), parts = f.t ? l.split(f.t) : l.trim().split(/\s+/); return parts.slice(k - 1, String(f.k).includes(',') ? +String(f.k).split(',')[1] : undefined).join(f.t || ' '); };
    const num = s => { const m = /^\s*-?\d+(\.\d+)?/.exec(s); return m ? parseFloat(m[0]) : 0; };
    const cmp = f.n ? (x, y) => num(key(x)) - num(key(y)) || (x < y ? -1 : x > y ? 1 : 0) : f.h ? (x, y) => hnum(key(x)) - hnum(key(y)) : (x, y) => { const kx = f.f ? key(x).toLowerCase() : key(x), ky = f.f ? key(y).toLowerCase() : key(y); return kx < ky ? -1 : kx > ky ? 1 : 0; };
    L.sort(cmp);
    if (f.r) L.reverse();
    if (f.u) L = L.filter((l, i) => i === 0 || cmp(l, L[i - 1]) !== 0);
    if (f.o) { const p = this.abs(f.o); const n = this.node(p) || this.mk(p, 'f', 0o644, this.user, ''); n.data = join(L); return 0; }
    this.out(join(L));
  };
  const hnum = s => { const m = /^\s*([\d.]+)([KMGT]?)/.exec(s); return m ? +m[1] * 1024 ** ' KMGT'.indexOf(m[2] || ' ') : 0; };
  C.uniq = function (a, input) {
    const [f, rest] = opts(a);
    const L = this.inputs(rest.slice(0, 1), input, 'uniq').flatMap(x => lines(x.data)), groups = [];
    L.forEach(l => { const g = groups[groups.length - 1]; const same = g && (f.i ? g[0].toLowerCase() === l.toLowerCase() : g[0] === l); if (same) g[1]++; else groups.push([l, 1]); });
    groups.forEach(([l, n]) => { if (f.d && n < 2) return; if (f.u && n > 1) return; this.out((f.c ? pad(n, 7) + ' ' : '') + l + '\n'); });
  };
  function ranges(spec) {
    return spec.split(',').map(r => { const m = /^(\d*)-(\d*)$/.exec(r); return m ? [m[1] ? +m[1] : 1, m[2] ? +m[2] : Infinity] : [+r, +r]; });
  }
  const inR = (rs, k) => rs.some(([x, y]) => k >= x && k <= y);
  C.cut = function (a, input) {
    const [f, rest] = opts(a, 'dfc');
    if (!f.f && !f.c) { this.eout('cut: you must specify a list of bytes, characters, or fields\n'); return 1; }
    const d = f.d === undefined ? '\t' : f.d;
    this.inputs(rest, input, 'cut').forEach(x => lines(x.data).forEach(l => {
      if (f.c) { const rs = ranges(f.c); this.out([...l].filter((_, i) => inR(rs, i + 1)).join('') + '\n'); return; }
      if (!l.includes(d)) { if (!f.s) this.out(l + '\n'); return; }
      const rs = ranges(f.f); this.out(l.split(d).filter((_, i) => inR(rs, i + 1)).join(d) + '\n');
    }));
  };
  function trSet(s) {
    s = s.replace(/\[:(\w+):\]/g, (_, c) => ({ upper: 'A-Z', lower: 'a-z', digit: '0-9', alpha: 'A-Za-z', alnum: 'A-Za-z0-9', space: ' \t\n', punct: '!-/:-@[-`{-~' }[c] || ''));
    s = unesc(s);
    let out = '';
    for (let i = 0; i < s.length; i++) {
      if (s[i + 1] === '-' && i + 2 < s.length) { for (let c = s.charCodeAt(i); c <= s.charCodeAt(i + 2); c++) out += String.fromCharCode(c); i += 2; } else out += s[i];
    }
    return out;
  }
  C.tr = function (a, input) {
    const [f, rest] = opts(a);
    const s1 = trSet(rest[0] || ''), s2 = trSet(rest[1] || '');
    let s = input;
    if (f.d) s = [...s].filter(c => !s1.includes(c)).join('');
    else if (s2) s = [...s].map(c => { const k = s1.indexOf(c); return k < 0 ? c : s2[Math.min(k, s2.length - 1)]; }).join('');
    if (f.s) { const set = s2 && !f.d ? s2 : s1; s = s.replace(/(.)\1+/g, (m, c) => set.includes(c) ? c : m); }
    this.out(s);
  };
  C.tee = function (a, input) {
    const [f, rest] = opts(a);
    rest.forEach(t => { const p = this.abs(t); let n = this.node(p); if (!n) { const d = this.node(dirName(p)); if (!d || !this.can(d, 'w')) { this.eout(`tee: ${t}: Permission denied\n`); return; } n = this.mk(p, 'f', 0o644, this.user, ''); } else if (!this.can(n, 'w')) { this.eout(`tee: ${t}: Permission denied\n`); return; } n.data = f.a ? n.data + input : input; n.mtime = this.now(); });
    this.out(input);
  };
  /* sed: s///flags, p, d, q, a, i, = with a line number, $ or /regex/ address, and -n, -i, -E, -e */
  C.sed = function (a, input) {
    const f = {}, rest = [], scripts = [];
    for (let i = 0; i < a.length; i++) {
      const x = a[i];
      if (x === '--') { rest.push(...a.slice(i + 1)); break; }
      if (/^--in-place(=.*)?$/.test(x)) { f.i = true; f.suffix = x.split('=')[1] || ''; continue; }
      if (/^-[A-Za-z]/.test(x)) {
        for (let j = 1; j < x.length; j++) {
          const ch = x[j];
          if (ch === 'e') { scripts.push(x.slice(j + 1) || a[++i] || ''); break; }
          if (ch === 'i') { f.i = true; f.suffix = x.slice(j + 1); break; }
          f[ch] = true;
        }
        continue;
      }
      rest.push(x);
    }
    if (!scripts.length) { if (rest.length) scripts.push(rest.shift()); else { this.eout('Usage: sed [OPTION]... {script} [input-file]...\n'); return 1; } }
    const cmds = [];
    scripts.join(';').split(/;(?![^/]*\/[gip0-9]*$)/).forEach(raw => {
      const s = raw.trim(); if (!s) return;
      const m = /^(\d+|\$|\/(?:[^/\\]|\\.)*\/)?(?:,(\d+|\$|\/(?:[^/\\]|\\.)*\/))?\s*(!?)\s*([spdqaic=y])(.*)$/.exec(s);
      if (!m) throw new Error(`-e expression #1: unknown command: \`${s[0]}'`);
      const addr = x => x === undefined ? null : x === '$' ? { last: true } : /^\d+$/.test(x) ? { n: +x } : { re: toRe(x.slice(1, -1), f.E || f.r) };
      const c = { a1: addr(m[1]), a2: addr(m[2]), neg: !!m[3], op: m[4], arg: m[5] };
      if (c.op === 's') {
        const dl = c.arg[0], parts = []; let cur = '', k = 1;
        for (; k < c.arg.length; k++) { if (c.arg[k] === '\\' && c.arg[k + 1] === dl) { cur += dl; k++; continue; } if (c.arg[k] === dl) { parts.push(cur); cur = ''; if (parts.length === 2) { k++; break; } continue; } cur += c.arg[k]; }
        const flags = c.arg.slice(k);
        c.re = toRe(parts[0], f.E || f.r, (flags.includes('g') ? 'g' : '') + (flags.includes('i') || flags.includes('I') ? 'i' : ''));
        c.rep = parts[1].replace(/\\(\d)/g, '$$$1').replace(/&/g, '$$&').replace(/\\n/g, '\n');
        c.print = flags.includes('p'); c.nth = (/\d+/.exec(flags) || [])[0];
      }
      if (c.op === 'y') { const dl = c.arg[0], [, from, to] = c.arg.split(dl); if ((from || '').length !== (to || '').length) throw new Error('-e expression #1: strings for `y\' command are different lengths'); c.map = {}; [...from].forEach((ch, k) => { c.map[ch] = to[k]; }); }
      cmds.push(c);
    });
    const files = rest.length ? rest : ['-'];
    files.forEach(fname => {
      const src = fname === '-' ? input : (() => { const n = this.node(this.abs(fname)); if (!n) { this.eout(`sed: can't read ${fname}: No such file or directory\n`); return null; } return n.data; })();
      if (src === null) return;
      const L = lines(src), out = [];
      const ranges2 = cmds.map(() => false);
      let quit = false;
      for (let i = 0; i < L.length && !quit; i++) {
        let line = L[i], del = false;
        const before = [], after = [];
        cmds.forEach((c, ci) => {
          if (del || quit) return;
          const hit = ad => ad === null ? true : ad.last ? i === L.length - 1 : ad.n !== undefined ? i + 1 === ad.n : ad.re.test(line);
          let on;
          if (c.a2) { if (ranges2[ci]) { on = true; if (hit(c.a2)) ranges2[ci] = false; } else if (c.a1 && hit(c.a1)) { on = true; ranges2[ci] = !(c.a2.n !== undefined && c.a2.n <= i + 1); } else on = false; }
          else on = hit(c.a1);
          if (c.neg) on = !on;
          if (!on) return;
          if (c.op === 's') { let n = 0; const nl = c.nth ? line.replace(new RegExp(c.re.source, c.re.flags + (c.re.flags.includes('g') ? '' : 'g')), (...mm) => (++n === +c.nth ? mm[0].replace(new RegExp(c.re.source, c.re.flags.replace('g', '')), c.rep) : mm[0])) : line.replace(c.re, c.rep); if (nl !== line || c.re.test(line)) { line = nl; if (c.print) before.push(line); } }
          else if (c.op === 'p') before.push(line);
          else if (c.op === 'y') line = [...line].map(ch => c.map[ch] ?? ch).join('');
          else if (c.op === 'c') { if (!c.a2 || !ranges2[ci]) before.push(c.arg.replace(/^\\?\s*/, '')); del = true; }
          else if (c.op === 'd') del = true;
          else if (c.op === 'q') { quit = true; }
          else if (c.op === '=') before.push(String(i + 1));
          else if (c.op === 'a') after.push(c.arg.replace(/^\\?\s*/, ''));
          else if (c.op === 'i') before.push(c.arg.replace(/^\\?\s*/, ''));
        });
        out.push(...before);
        if (!del && !f.n) out.push(line);
        out.push(...after.filter((x, k) => !(f.n === undefined && false)));
      }
      if (f.i && fname !== '-') { const p0 = this.abs(fname), n = this.node(p0); if (f.suffix) { const b = this.mk(p0 + f.suffix, 'f', n.mode, this.user, n.data); b.mtime = n.mtime; } n.data = join(out); n.mtime = this.now(); } else this.out(join(out));
    });
  };
  /* ---------- awk: a small but real interpreter (POSIX awk language, see the awk lesson) ----------
     Values are numbers, strings, or {sn} for input text that looks like a number (fields, split pieces, -v values),
     which compare as numbers, as POSIX "strnum" values do. */
  const AWK_KW = new Set(['BEGIN', 'END', 'function', 'func', 'if', 'else', 'while', 'for', 'do', 'in', 'break', 'continue', 'next', 'nextfile', 'exit', 'return', 'delete', 'print', 'printf', 'getline']);
  const AWK_FN = new Set(['length', 'substr', 'index', 'split', 'sub', 'gsub', 'match', 'sprintf', 'toupper', 'tolower', 'int', 'sqrt', 'exp', 'log', 'sin', 'cos', 'atan2', 'rand', 'srand', 'system', 'close', 'fflush']);
  function awkLex(src) {
    const t = []; let i = 0;
    const operand = () => { const p = t[t.length - 1]; return p && (p.k === 'num' || p.k === 'str' || p.k === 'name' || p.k === 'ere' || p.k === 'fn' && false || [')', ']', '$', '++', '--'].includes(p.v) && p.k === 'op'); };
    while (i < src.length) {
      const c = src[i];
      if (c === ' ' || c === '\t' || c === '\r') { i++; continue; }
      if (c === '\\' && src[i + 1] === '\n') { i += 2; continue; }
      if (c === '#') { while (i < src.length && src[i] !== '\n') i++; continue; }
      if (c === '\n') { t.push({ k: 'nl', v: '\n' }); i++; continue; }
      if (c === '"') {
        let j = i + 1, s = '';
        while (j < src.length && src[j] !== '"') { if (src[j] === '\\') { const e = src[j + 1]; s += { n: '\n', t: '\t', r: '\r', '\\': '\\', '"': '"', '/': '/', a: '\x07', b: '\b', f: '\f', v: '\v' }[e] ?? '\\' + e; j += 2; continue; } s += src[j++]; }
        if (j >= src.length) throw new Error('non-terminated string');
        t.push({ k: 'str', v: s }); i = j + 1; continue;
      }
      if (c === '/' && !operand()) {
        let j = i + 1, s = '';
        while (j < src.length && src[j] !== '/') { if (src[j] === '\\' && src[j + 1] === '/') { s += '/'; j += 2; continue; } if (src[j] === '\\') { s += src[j] + src[j + 1]; j += 2; continue; } if (src[j] === '\n') throw new Error('non-terminated regular expression'); s += src[j++]; }
        t.push({ k: 'ere', v: s }); i = j + 1; continue;
      }
      let m = /^(\d+\.?\d*([eE][-+]?\d+)?|\.\d+([eE][-+]?\d+)?)/.exec(src.slice(i));
      if (m) { t.push({ k: 'num', v: +m[0] }); i += m[0].length; continue; }
      m = /^[A-Za-z_]\w*/.exec(src.slice(i));
      if (m) {
        const w = m[0]; i += w.length;
        if (AWK_KW.has(w)) t.push({ k: 'kw', v: w });
        else if (AWK_FN.has(w)) t.push({ k: 'bi', v: w });
        else if (src[i] === '(') t.push({ k: 'fn', v: w });
        else t.push({ k: 'name', v: w });
        continue;
      }
      m = /^(\+=|-=|\*=|\/=|%=|\^=|==|<=|>=|!=|\+\+|--|&&|\|\||!~|>>|\*\*=|\*\*|[{}()[\];,+\-*/%^!<>|?:~$=])/.exec(src.slice(i));
      if (!m) throw new Error(`syntax error at source line 1: unexpected character '${c}'`);
      t.push({ k: 'op', v: m[0] === '**' ? '^' : m[0] === '**=' ? '^=' : m[0] }); i += m[0].length;
    }
    t.push({ k: 'eof', v: '' });
    return t;
  }
  function awkParse(toks) {
    let i = 0;
    const peek = (o = 0) => toks[i + o], is = (v, k) => toks[i].v === v && (!k || toks[i].k === k) && (toks[i].k === 'op' || toks[i].k === 'kw' || k);
    const eat = v => { if (toks[i].v !== v) throw new Error(`syntax error near "${toks[i].v === '\n' ? 'newline' : toks[i].v || 'end of program'}"`); return toks[i++]; };
    const nls = () => { while (toks[i].k === 'nl') i++; };
    const term = () => { let any = false; while (toks[i].k === 'nl' || is(';')) { i++; any = true; } return any; };
    const items = [], funcs = {};
    const expr = (noIn, noGt) => ternary(noIn, noGt);
    const ternary = (noIn, noGt) => {
      const c = orE(noIn, noGt);
      if (is('?')) { i++; nls(); const a = ternary(noIn, noGt); nls(); eat(':'); nls(); const b = ternary(noIn, noGt); return { t: '?:', c, a, b }; }
      if (toks[i].k === 'op' && ['=', '+=', '-=', '*=', '/=', '%=', '^='].includes(toks[i].v) && (c.t === 'var' || c.t === 'idx' || c.t === 'fld')) { const op = toks[i++].v; nls(); return { t: 'asg', op, l: c, r: ternary(noIn, noGt) }; }
      return c;
    };
    const orE = (noIn, noGt) => { let l = andE(noIn, noGt); while (is('||')) { i++; nls(); l = { t: '||', l, r: andE(noIn, noGt) }; } return l; };
    const andE = (noIn, noGt) => { let l = inE(noIn, noGt); while (is('&&')) { i++; nls(); l = { t: '&&', l, r: inE(noIn, noGt) }; } return l; };
    const inE = (noIn, noGt) => { let l = matchE(noIn, noGt); while (!noIn && toks[i].k === 'kw' && toks[i].v === 'in') { i++; l = { t: 'in', k: l, a: toks[i++].v }; } return l; };
    const matchE = (noIn, noGt) => { let l = relE(noIn, noGt); while (is('~') || is('!~')) { const op = toks[i++].v; l = { t: op, l, r: relE(noIn, noGt) }; } return l; };
    const relE = (noIn, noGt) => {
      const l = catE(noIn, noGt);
      if (toks[i].k === 'op' && ['<', '<=', '==', '!=', '>=', '>'].includes(toks[i].v) && !(noGt && toks[i].v === '>')) { const op = toks[i++].v; return { t: 'cmp', op, l, r: catE(noIn, noGt) }; }
      return l;
    };
    const startsOperand = () => { const x = toks[i]; return x.k === 'num' || x.k === 'str' || x.k === 'ere' || x.k === 'name' || x.k === 'fn' || x.k === 'bi' || x.k === 'op' && ['$', '!', '(', '-', '+', '++', '--'].includes(x.v); };
    const catE = (noIn, noGt) => { let l = addE(); while (startsOperand() && !(toks[i].k === 'kw' && toks[i].v === 'in')) { l = { t: 'cat', l, r: addE() }; } return l; };
    const addE = () => { let l = mulE(); while (is('+') || is('-')) { const op = toks[i++].v; l = { t: 'bin', op, l, r: mulE() }; } return l; };
    const mulE = () => { let l = unE(); while (is('*') || is('/') || is('%')) { const op = toks[i++].v; l = { t: 'bin', op, l, r: unE() }; } return l; };
    const unE = () => { if (is('!')) { i++; return { t: '!', e: unE() }; } if (is('-')) { i++; return { t: 'neg', e: unE() }; } if (is('+')) { i++; return { t: 'pos', e: unE() }; } return powE(); };
    const powE = () => { const b = postE(); if (is('^')) { i++; return { t: 'bin', op: '^', l: b, r: unE() }; } return b; };
    const postE = () => {
      if (is('++') || is('--')) { const op = toks[i++].v; return { t: 'pre', op, e: postE() }; }
      const e = prim();
      if ((is('++') || is('--')) && (e.t === 'var' || e.t === 'idx' || e.t === 'fld')) { const op = toks[i++].v; return { t: 'post', op, e }; }
      return e;
    };
    const args = () => { eat('('); const a = []; nls(); if (!is(')')) { a.push(expr()); nls(); while (is(',')) { i++; nls(); a.push(expr()); nls(); } } eat(')'); return a; };
    const subscript = () => { eat('['); const a = [expr()]; while (is(',')) { i++; a.push(expr()); } eat(']'); return a; };
    const prim = () => {
      const x = toks[i];
      if (x.k === 'num') { i++; return { t: 'num', v: x.v }; }
      if (x.k === 'str') { i++; return { t: 'str', v: x.v }; }
      if (x.k === 'ere') { i++; return { t: 'ere', v: x.v }; }
      if (x.k === 'op' && x.v === '$') { i++; const e = (is('++') || is('--')) ? postE() : prim(); return { t: 'fld', e }; }
      if (x.k === 'op' && x.v === '(') {
        i++; const e = expr();
        if (is(',')) { const list = [e]; while (is(',')) { i++; list.push(expr()); } eat(')'); if (toks[i].k === 'kw' && toks[i].v === 'in') { i++; return { t: 'in', k: { t: 'group', list }, a: toks[i++].v }; } return { t: 'group', list }; }
        eat(')'); return { t: 'grp', e };
      }
      if (x.k === 'bi') {
        i++;
        if (x.v === 'length' && !is('(')) return { t: 'call', f: 'length', a: [] };
        return { t: 'call', f: x.v, a: args() };
      }
      if (x.k === 'fn') { i++; return { t: 'ucall', f: x.v, a: args() }; }
      if (x.k === 'name') { i++; if (is('[')) return { t: 'idx', a: x.v, s: subscript() }; return { t: 'var', v: x.v }; }
      if (x.k === 'kw' && x.v === 'getline') { i++; return { t: 'getline' }; }
      throw new Error(`syntax error near "${x.v === '\n' ? 'newline' : x.v || 'end of program'}"`);
    };
    const simpleStmt = () => {
      const x = toks[i];
      if (x.k === 'kw' && (x.v === 'print' || x.v === 'printf')) {
        i++; let list = [];
        if (!(toks[i].k === 'nl' || is(';') || is('}') || is('>') || is('>>') || is('|') || toks[i].k === 'eof')) {
          if (is('(')) { const save = i; try { i++; const l = [expr(false, false)]; while (is(',')) { i++; l.push(expr(false, false)); } eat(')'); if (toks[i].k === 'nl' || is(';') || is('}') || is('>') || is('>>') || is('|') || toks[i].k === 'eof') list = l; else { i = save; list = null; } } catch (e) { i = save; list = null; } }
          if (!list || !list.length) { list = [expr(false, true)]; while (is(',')) { i++; nls(); list.push(expr(false, true)); } }
        }
        let to = null;
        if (is('>') || is('>>') || is('|')) { const op = toks[i++].v; to = { op, e: catE(false, true) }; }
        return { t: x.v, list, to };
      }
      if (x.k === 'kw' && x.v === 'next') { i++; return { t: 'next' }; }
      if (x.k === 'kw' && x.v === 'exit') { i++; const e = toks[i].k === 'nl' || is(';') || is('}') || toks[i].k === 'eof' ? null : expr(); return { t: 'exit', e }; }
      if (x.k === 'kw' && x.v === 'return') { i++; const e = toks[i].k === 'nl' || is(';') || is('}') ? null : expr(); return { t: 'return', e }; }
      if (x.k === 'kw' && x.v === 'break') { i++; return { t: 'break' }; }
      if (x.k === 'kw' && x.v === 'continue') { i++; return { t: 'continue' }; }
      if (x.k === 'kw' && x.v === 'delete') { i++; const a = toks[i++].v; return { t: 'delete', a, s: is('[') ? subscript() : null }; }
      return { t: 'expr', e: expr() };
    };
    const stmt = () => {
      nls();
      const x = toks[i];
      if (is('{')) { i++; const b = block(); return b; }
      if (x.k === 'kw' && x.v === 'if') { i++; eat('('); const c = expr(); eat(')'); nls(); const a = stmt(); const save = i; term(); if (toks[i].k === 'kw' && toks[i].v === 'else') { i++; nls(); return { t: 'if', c, a, b: stmt() }; } i = save; return { t: 'if', c, a, b: null }; }
      if (x.k === 'kw' && x.v === 'while') { i++; eat('('); const c = expr(); eat(')'); if (is(';')) { i++; return { t: 'while', c, b: { t: 'block', list: [] } }; } nls(); return { t: 'while', c, b: stmt() }; }
      if (x.k === 'kw' && x.v === 'do') { i++; nls(); const b = stmt(); term(); eat('while'); eat('('); const c = expr(); eat(')'); return { t: 'do', c, b }; }
      if (x.k === 'kw' && x.v === 'for') {
        i++; eat('(');
        if (toks[i].k === 'name' && toks[i + 1].k === 'kw' && toks[i + 1].v === 'in' && toks[i + 2].k === 'name' && toks[i + 3].v === ')') { const v = toks[i].v, a = toks[i + 2].v; i += 4; nls(); return { t: 'forin', v, a, b: stmt() }; }
        const init = is(';') ? null : simpleStmt(); eat(';'); nls();
        const c = is(';') ? null : expr(); eat(';'); nls();
        const inc = is(')') ? null : simpleStmt(); eat(')');
        if (is(';')) { i++; return { t: 'for', init, c, inc, b: { t: 'block', list: [] } }; }
        nls(); return { t: 'for', init, c, inc, b: stmt() };
      }
      if (is(';')) { i++; return { t: 'block', list: [] }; }
      const s = simpleStmt();
      if (!(term() || is('}') || toks[i].k === 'eof')) throw new Error(`syntax error near "${toks[i].v}"`);
      return s;
    };
    const block = () => { const list = []; nls(); while (!is('}')) { if (toks[i].k === 'eof') throw new Error('syntax error: a { was not closed'); list.push(stmt()); nls(); while (is(';')) { i++; nls(); } } eat('}'); return { t: 'block', list }; };
    term();
    while (toks[i].k !== 'eof') {
      const x = toks[i];
      if (x.k === 'kw' && (x.v === 'function' || x.v === 'func')) {
        i++; const name = toks[i++].v; eat('('); const params = []; while (!is(')')) { params.push(toks[i++].v); if (is(',')) { i++; nls(); } } eat(')'); nls(); eat('{');
        funcs[name] = { params, body: block() };
      } else if (x.k === 'kw' && (x.v === 'BEGIN' || x.v === 'END')) { i++; nls(); eat('{'); items.push({ kind: x.v, body: block() }); }
      else {
        let pat = null, pat2 = null;
        if (!is('{')) { pat = expr(); if (is(',')) { i++; nls(); pat2 = expr(); } }
        const body = is('{') ? (i++, block()) : null;
        items.push({ kind: 'main', pat, pat2, body, inRange: false });
      }
      term();
    }
    return { items, funcs };
  }
  const awkFmtG = (v, p) => {
    if (!isFinite(v)) return isNaN(v) ? 'nan' : v < 0 ? '-inf' : 'inf';
    if (v === 0) return '0';
    const e = Math.floor(Math.log10(Math.abs(v)));
    if (e < -4 || e >= p) { let [m, x] = v.toExponential(Math.max(p - 1, 0)).split('e'); if (m.includes('.')) m = m.replace(/0+$/, '').replace(/\.$/, ''); const n = +x; return m + 'e' + (n < 0 ? '-' : '+') + String(Math.abs(n)).padStart(2, '0'); }
    let s = v.toFixed(Math.max(p - 1 - e, 0)); if (s.includes('.')) s = s.replace(/0+$/, '').replace(/\.$/, ''); return s;
  };
  function awkSprintf(fmt, args, toNum, toStr) {
    let k = 0;
    return fmt.replace(/%([-+ #0]*)(\*|\d+)?(?:\.(\*|\d+))?([diouxXeEfFgGcs%])/g, (all, fl, w, pr, ty) => {
      if (ty === '%') return '%';
      if (w === '*') w = toNum(args[k++]); if (pr === '*') pr = toNum(args[k++]);
      const a = args[k++]; let s;
      const neg = fl.includes('-'), zero = fl.includes('0') && !neg, plus = fl.includes('+'), sp = fl.includes(' ');
      if ('di'.includes(ty)) { const n = Math.trunc(toNum(a)); s = String(Math.abs(n)); if (pr !== undefined) s = s.padStart(+pr, '0'); s = (n < 0 ? '-' : plus ? '+' : sp ? ' ' : '') + s; }
      else if ('ouxX'.includes(ty)) { const n = Math.trunc(toNum(a)) >>> 0; s = n.toString({ o: 8, u: 10, x: 16, X: 16 }[ty]); if (ty === 'X') s = s.toUpperCase(); }
      else if ('eE'.includes(ty)) { const n = toNum(a); let [m, x] = n.toExponential(pr === undefined ? 6 : +pr).split('e'); s = m + 'e' + (+x < 0 ? '-' : '+') + String(Math.abs(+x)).padStart(2, '0'); if (ty === 'E') s = s.toUpperCase(); if (n >= 0 && plus) s = '+' + s; }
      else if ('fF'.includes(ty)) { const n = toNum(a); s = n.toFixed(pr === undefined ? 6 : +pr); if (n >= 0 && plus) s = '+' + s; else if (n >= 0 && sp) s = ' ' + s; }
      else if ('gG'.includes(ty)) { s = awkFmtG(toNum(a), pr === undefined ? 6 : Math.max(+pr, 1)); if (ty === 'G') s = s.toUpperCase(); }
      else if (ty === 'c') { s = typeof a === 'number' ? String.fromCharCode(a) : toStr(a).charAt(0); }
      else { s = toStr(a); if (pr !== undefined) s = s.slice(0, +pr); }
      if (w !== undefined && s.length < +w) s = neg ? s.padEnd(+w) : zero && !'sc'.includes(ty) ? (s[0] === '-' || s[0] === '+' ? s[0] + s.slice(1).padStart(+w - 1, '0') : s.padStart(+w, '0')) : s.padStart(+w);
      return s;
    });
  }
  C.awk = function (a, input) {
    const pre = [], files = []; let fs = null, progSrc = null;
    for (let i = 0; i < a.length; i++) {
      const x = a[i];
      if (x === '--') { files.push(...a.slice(i + 1)); break; }
      if (progSrc === null && x === '-F') { fs = a[++i]; continue; }
      if (progSrc === null && /^-F./.test(x)) { fs = x.slice(2); continue; }
      if (progSrc === null && x === '-v') { pre.push(a[++i]); continue; }
      if (progSrc === null && /^-v./.test(x)) { pre.push(x.slice(2)); continue; }
      if (progSrc === null && x === '-f') { const n = this.node(this.abs(a[++i] || '')); if (!n) { this.eout(`awk: can't open file ${a[i]}\n`); return 2; } progSrc = n.data; continue; }
      if (progSrc === null) { progSrc = x; continue; }
      files.push(x);
    }
    if (progSrc === null) { this.eout('usage: awk [-F fs][-v var=value][prog | -f progfile][file ...]\n'); return 2; }
    let P;
    try { P = awkParse(awkLex(progSrc)); } catch (e) { this.eout(`awk: ${e.message}\n awk: ${progSrc.split('\n')[0]}\n`); return 2; }
    const sn = s => ({ sn: String(s) }), UN = { sn: '', un: true };
    const looksNum = s => /^\s*[-+]?(\d+\.?\d*([eE][-+]?\d+)?|\.\d+([eE][-+]?\d+)?)\s*$/.test(s);
    const unesc = s => s.replace(/\\(.)/g, (m, c) => ({ n: '\n', t: '\t', '\\': '\\' }[c] ?? m));
    const V = { NR: 0, FNR: 0, NF: 0, FS: fs === null ? ' ' : fs === 't' ? '\t' : unesc(fs), OFS: ' ', ORS: '\n', RS: '\n', FILENAME: '', SUBSEP: '\x1c', RSTART: 0, RLENGTH: -1, CONVFMT: '%.6g', OFMT: '%.6g', ENVIRON: Object.assign({}, this.vars) };
    pre.forEach(p => { const k = p.indexOf('='); if (k > 0) V[p.slice(0, k)] = sn(unesc(p.slice(k + 1))); });
    const A = {}, fns = P.funcs;
    let fields = [''], out = '';
    const pipes = {}, filesOut = {};
    const num = v => typeof v === 'number' ? v : (() => { const m = /^\s*[-+]?(\d+\.?\d*([eE][-+]?\d+)?|\.\d+([eE][-+]?\d+)?)/.exec(typeof v === 'object' && v !== null ? v.sn : String(v ?? '')); return m ? +m[0] : 0; })();
    const str = (v, ofmt) => typeof v === 'number' ? (Number.isInteger(v) && Math.abs(v) < 1e16 ? String(v) : awkSprintf(ofmt ? String(V.OFMT) : String(V.CONVFMT), [v], num, x => String(x))) : typeof v === 'object' && v !== null ? v.sn : String(v ?? '');
    const truth = v => typeof v === 'number' ? v !== 0 : typeof v === 'object' && v !== null ? (looksNum(v.sn) ? num(v) !== 0 : v.sn !== '') : v !== '' && v !== undefined;
    const isNumish = v => typeof v === 'number' || (typeof v === 'object' && v !== null && (v.un || looksNum(v.sn))) || v === undefined;
    const splitRec = (s, f) => {
      if (f === ' ') return s.split(/[ \t\n]+/).filter(x => x !== '');
      if (s === '') return [];
      if (f.length === 1 && f !== '\\') return s.split(f);
      return s.split(LXSH_RE(f));
    };
    const LXSH_RE = (p, g) => toRe(p, true, g || '');
    const setRecord = s => { fields = [s].concat(splitRec(s, str(V.FS))); V.NF = fields.length - 1; };
    const rebuild = () => { fields[0] = fields.slice(1).map(x => str(x)).join(str(V.OFS)); };
    const getF = n => { n = Math.trunc(num(n)); if (n < 0) throw new Error(`trying to access out of range field ${n}`); return n === 0 ? sn(fields[0]) : n < fields.length ? sn(str(fields[n])) : UN; };
    const setF = (n, v) => { n = Math.trunc(num(n)); if (n === 0) { setRecord(str(v)); return; } while (fields.length <= n) fields.push(''); fields[n] = str(v); V.NF = Math.max(V.NF, n); if (fields.length - 1 > V.NF) fields.length = V.NF + 1; rebuild(); };
    const key = s => s.map(x => str(ev(x))).join(str(V.SUBSEP));
    const scopes = [];
    const getVar = n => { for (let k = scopes.length - 1; k >= 0 && k >= scopes.length - 1; k--) if (n in scopes[k]) return scopes[k][n]; return n === 'NF' ? V.NF : V[n]; };
    const setVar = (n, v) => { const sc = scopes[scopes.length - 1]; if (sc && n in sc) { sc[n] = v; return; } if (n === 'NF') { V.NF = Math.trunc(num(v)); fields.length = Math.min(fields.length, V.NF + 1); while (fields.length <= V.NF) fields.push(''); rebuild(); return; } V[n] = v; };
    const arr = n => { const sc = scopes[scopes.length - 1]; if (sc && n in sc) { if (typeof sc[n] !== 'object' || sc[n] === null || sc[n].sn !== undefined || sc[n] === '') sc[n] = sc[n] && sc[n].__arr ? sc[n] : { __arr: true, m: new Map() }; return sc[n].m; } if (n === 'ENVIRON') { if (!A.ENVIRON) A.ENVIRON = new Map(Object.entries(V.ENVIRON).map(([k, v]) => [k, sn(v)])); } return A[n] || (A[n] = new Map()); };
    const lval = (e, v) => { if (e.t === 'var') setVar(e.v, v); else if (e.t === 'idx') arr(e.a).set(key(e.s), v); else if (e.t === 'fld') setF(ev(e.e), v); return v; };
    const reOf = e => e.t === 'ere' ? LXSH_RE(e.v) : LXSH_RE(str(ev(e)));
    const self = this;
    const ev = e => {
      switch (e.t) {
        case 'num': return e.v;
        case 'str': return e.v;
        case 'ere': return LXSH_RE(e.v).test(fields[0]) ? 1 : 0;
        case 'grp': return ev(e.e);
        case 'group': return e.list.map(x => str(ev(x))).join(str(V.SUBSEP));
        case 'var': { const v = getVar(e.v); return v === undefined ? UN : v; }
        case 'idx': { const m = arr(e.a), k = key(e.s); if (!m.has(k)) m.set(k, UN); return m.get(k); }
        case 'fld': return getF(ev(e.e));
        case 'in': { const k = e.k.t === 'group' ? e.k.list.map(x => str(ev(x))).join(str(V.SUBSEP)) : str(ev(e.k)); return arr(e.a).has(k) ? 1 : 0; }
        case 'asg': {
          if (e.op === '=') return lval(e.l, (() => { const v = ev(e.r); return typeof v === 'object' && v !== null && v.__arr ? '' : v; })());
          const a = num(ev(e.l)), b = num(ev(e.r));
          return lval(e.l, { '+=': a + b, '-=': a - b, '*=': a * b, '/=': (() => { if (b === 0) throw new Error('division by zero in /='); return a / b; })(), '%=': a % b, '^=': a ** b }[e.op]);
        }
        case '?:': return truth(ev(e.c)) ? ev(e.a) : ev(e.b);
        case '||': return truth(ev(e.l)) || truth(ev(e.r)) ? 1 : 0;
        case '&&': return truth(ev(e.l)) && truth(ev(e.r)) ? 1 : 0;
        case '~': case '!~': { const s = str(ev(e.l)); return reOf(e.r).test(s) === (e.t === '~') ? 1 : 0; }
        case 'cmp': {
          const l = ev(e.l), r = ev(e.r);
          const both = isNumish(l) && isNumish(r) && !(typeof l === 'string' && l !== '') && !(typeof r === 'string' && r !== '');
          const x = both ? num(l) : str(l), y = both ? num(r) : str(r);
          return { '<': x < y, '<=': x <= y, '==': x === y, '!=': x !== y, '>=': x >= y, '>': x > y }[e.op] ? 1 : 0;
        }
        case 'cat': return str(ev(e.l)) + str(ev(e.r));
        case 'bin': {
          const a = num(ev(e.l)), b = num(ev(e.r));
          if ((e.op === '/' || e.op === '%') && b === 0) throw new Error('division by zero');
          return { '+': a + b, '-': a - b, '*': a * b, '/': a / b, '%': a % b, '^': a ** b }[e.op];
        }
        case '!': return truth(ev(e.e)) ? 0 : 1;
        case 'neg': return -num(ev(e.e));
        case 'pos': return num(ev(e.e));
        case 'pre': { const v = num(ev(e.e)) + (e.op === '++' ? 1 : -1); lval(e.e, v); return v; }
        case 'post': { const v = num(ev(e.e)); lval(e.e, v + (e.op === '++' ? 1 : -1)); return v; }
        case 'getline': return 0;
        case 'ucall': {
          const fd = fns[e.f]; if (!fd) throw new Error(`calling undefined function ${e.f}`);
          const sc = {}; fd.params.forEach((p, k) => { const x = e.a[k]; if (x && x.t === 'var' && (A[x.v] || (scopes.length && scopes[scopes.length - 1][x.v] && scopes[scopes.length - 1][x.v].__arr))) sc[p] = { __arr: true, m: arr(x.v) }; else sc[p] = x ? ev(x) : ''; });
          if (scopes.length > 200) throw new Error('function call nesting too deep');
          scopes.push(sc);
          try { run(fd.body); } catch (x) { if (x && x.awkRet !== undefined) return x.awkRet; throw x; } finally { scopes.pop(); }
          return '';
        }
        case 'call': {
          const g = e.a;
          switch (e.f) {
            case 'length': { if (!g.length) return fields[0].length; if (g[0].t === 'var' && (A[g[0].v] || (scopes.length && scopes[scopes.length - 1][g[0].v] && scopes[scopes.length - 1][g[0].v].__arr))) return arr(g[0].v).size; return str(ev(g[0])).length; }
            case 'substr': { const s = str(ev(g[0])); let m = Math.round(num(ev(g[1]))), n = g[2] ? Math.round(num(ev(g[2]))) : Infinity; let st = m, en = n === Infinity ? Infinity : m + n; st = Math.max(st, 1); en = Math.min(en, s.length + 1); return en > st ? s.slice(st - 1, en - 1) : ''; }
            case 'index': { return str(ev(g[0])).indexOf(str(ev(g[1]))) + 1; }
            case 'split': { const s = str(ev(g[0])), m = arr(g[1].v), sep = g[2] ? (g[2].t === 'ere' ? null : str(ev(g[2]))) : str(V.FS); m.clear(); const parts = g[2] && g[2].t === 'ere' ? (s === '' ? [] : s.split(LXSH_RE(g[2].v))) : splitRec(s, sep); parts.forEach((p, k) => m.set(String(k + 1), sn(p))); return parts.length; }
            case 'sub': case 'gsub': {
              const re = reOf(g[0]), target = g[2] || { t: 'fld', e: { t: 'num', v: 0 } }, s = str(ev(target)), rep = str(ev(g[1]));
              let n = 0;
              const R = new RegExp(re.source, re.flags.replace('g', '') + (e.f === 'gsub' ? 'g' : ''));
              const res = s.replace(R, m => { n++; return rep.replace(/\\\\&|\\&|&/g, x => x === '&' ? m : x === '\\&' ? '&' : '\\&'); });
              if (n) lval(target, res);
              return n;
            }
            case 'match': { const s = str(ev(g[0])), m = reOf(g[1]).exec(s); V.RSTART = m ? m.index + 1 : 0; V.RLENGTH = m ? m[0].length : -1; return V.RSTART; }
            case 'sprintf': return awkSprintf(str(ev(g[0])), g.slice(1).map(ev), num, str);
            case 'toupper': return str(ev(g[0])).toUpperCase();
            case 'tolower': return str(ev(g[0])).toLowerCase();
            case 'int': return Math.trunc(num(ev(g[0])));
            case 'sqrt': return Math.sqrt(num(ev(g[0])));
            case 'exp': return Math.exp(num(ev(g[0])));
            case 'log': return Math.log(num(ev(g[0])));
            case 'sin': return Math.sin(num(ev(g[0])));
            case 'cos': return Math.cos(num(ev(g[0])));
            case 'atan2': return Math.atan2(num(ev(g[0])), num(ev(g[1])));
            case 'rand': return Math.random();
            case 'srand': return 0;
            case 'system': { const c = str(ev(g[0])); self.runSrc(c, true); return self.last; }
            case 'close': case 'fflush': return 0;
          }
          return '';
        }
      }
      throw new Error('cannot evaluate ' + e.t);
    };
    const emit = (s, to) => {
      if (!to) { out += s; return; }
      const dest = str(ev(to.e));
      if (to.op === '|') { pipes[dest] = (pipes[dest] || '') + s; return; }
      if (dest === '/dev/stdout' || dest === '-') { out += s; return; }
      if (dest === '/dev/stderr') { self.eout(s); return; }
      const p = self.abs(dest);
      let n = self.node(p);
      if (!(dest in filesOut)) { if (!n) n = self.mk(p, 'f', 0o666 & ~self.umask, self.user, ''); if (to.op === '>') n.data = ''; filesOut[dest] = true; }
      n.data += s; n.mtime = self.now();
    };
    const run = s => {
      switch (s.t) {
        case 'block': s.list.forEach(run); return;
        case 'expr': ev(s.e); return;
        case 'print': emit((s.list.length ? s.list.map(x => str(ev(x), true)).join(str(V.OFS)) : fields[0]) + str(V.ORS), s.to); return;
        case 'printf': { if (!s.list.length) throw new Error('printf: no format'); const vals = s.list.map(ev); emit(awkSprintf(str(vals[0]), vals.slice(1), num, str), s.to); return; }
        case 'if': if (truth(ev(s.c))) run(s.a); else if (s.b) run(s.b); return;
        case 'while': { let n = 0; while (truth(ev(s.c))) { if (++n > 1e6) throw new Error('loop ran too long'); try { run(s.b); } catch (x) { if (x === BRK) break; if (x === CNT) continue; throw x; } } return; }
        case 'do': { let n = 0; do { if (++n > 1e6) throw new Error('loop ran too long'); try { run(s.b); } catch (x) { if (x === BRK) break; if (x === CNT) continue; throw x; } } while (truth(ev(s.c))); return; }
        case 'for': { let n = 0; if (s.init) run(s.init); while (!s.c || truth(ev(s.c))) { if (++n > 1e6) throw new Error('loop ran too long'); try { run(s.b); } catch (x) { if (x === BRK) break; if (x !== CNT) throw x; } if (s.inc) run(s.inc); } return; }
        case 'forin': { for (const k of [...arr(s.a).keys()]) { setVar(s.v, looksNum(k) ? sn(k) : k); try { run(s.b); } catch (x) { if (x === BRK) break; if (x === CNT) continue; throw x; } } return; }
        case 'next': throw NXT;
        case 'exit': throw { awkExit: s.e ? Math.trunc(num(ev(s.e))) : null };
        case 'return': throw { awkRet: s.e ? ev(s.e) : '' };
        case 'break': throw BRK;
        case 'continue': throw CNT;
        case 'delete': { const m = arr(s.a); if (s.s) m.delete(key(s.s)); else m.clear(); return; }
      }
    };
    const BRK = { brk: 1 }, CNT = { cnt: 1 }, NXT = { nxt: 1 };
    let code = 0, exiting = false;
    const guard = f => { try { f(); } catch (x) { if (x && x.awkExit !== undefined) { exiting = true; if (x.awkExit !== null) code = x.awkExit; return; } throw x; } };
    try {
      P.items.filter(it => it.kind === 'BEGIN').forEach(it => { if (!exiting) guard(() => run(it.body)); });
      const mains = P.items.filter(it => it.kind === 'main');
      const ends = P.items.filter(it => it.kind === 'END');
      if (!exiting && (mains.length || ends.length)) {
        const srcs = files.length ? files : ['-'];
        for (const fn of srcs) {
          if (exiting) break;
          let src;
          if (fn === '-') src = input || '';
          else { const n = this.node(this.abs(fn)); if (!n || n.type === 'd') { this.eout(`awk: cannot open "${fn}" (${n ? 'Is a directory' : 'No such file or directory'})\n`); code = 2; continue; } if (!this.can(n, 'r')) { this.eout(`awk: cannot open "${fn}" (Permission denied)\n`); code = 2; continue; } src = n.data; }
          V.FILENAME = fn === '-' ? '' : fn; V.FNR = 0;
          const recs = str(V.RS) === '' ? src.split(/\n\n+/).map(x => x.replace(/^\n+|\n+$/g, '')).filter(Boolean) : lines(src);
          for (const r of recs) {
            if (exiting) break;
            V.NR++; V.FNR++;
            setRecord(r);
            try {
              guard(() => {
                for (const it of mains) {
                  let on;
                  if (it.pat2) { if (it.inRange) { on = true; if (truth(ev(it.pat2))) it.inRange = false; } else if (truth(ev(it.pat))) { on = true; it.inRange = !truth(ev(it.pat2)); } else on = false; }
                  else on = !it.pat || truth(ev(it.pat));
                  if (!on) continue;
                  if (it.body) run(it.body); else out += fields[0] + str(V.ORS);
                }
              });
            } catch (x) { if (x !== NXT) throw x; }
          }
        }
      }
      exiting = false;
      ends.forEach(it => { if (!exiting) guard(() => run(it.body)); });
    } catch (e) {
      this.out(out); out = '';
      if (e === BRK || e === CNT || e === NXT) { this.eout('awk: break, continue or next used outside a loop\n'); return 2; }
      this.eout(`awk: ${e && e.message ? e.message : e}\n`); return 2;
    }
    this.out(out);
    Object.entries(pipes).forEach(([cmd, data]) => { try { this.exec(this.parse(this.lex(cmd)), data); } catch (e) { this.eout(`awk: ${e.message}\n`); } });
    return code;
  };
  C.chmod = function (a) {
    const [f, rest] = opts(a.map(x => /^[-+=][rwxXst]+$/.test(x) ? '\u0001' + x : x));
    const args = rest.map(x => x.replace('\u0001', ''));
    if (args.length < 2) { this.eout(`chmod: missing operand\n`); return 1; }
    const mode = args.shift(); let code = 0;
    const apply = (n, t) => {
      if (n.owner !== this.user && this.user !== 'root') { this.eout(`chmod: changing permissions of '${t}': Operation not permitted\n`); code = 1; return; }
      if (/^[0-7]{1,4}$/.test(mode)) { n.mode = parseInt(mode, 8) | (n.type === 'd' && mode.length < 4 ? n.mode & 0o6000 : 0); }
      else {
        for (const cl of mode.split(',')) {
          const m = /^([ugoa]*)([-+=])([rwxXst]*)$/.exec(cl);
          if (!m) { this.eout(`chmod: invalid mode: '${mode}'\n`); code = 1; return; }
          const who = m[1] || 'a', op = m[2];
          let bits = 0;
          [...m[3]].forEach(p => {
            const x = p === 'X' ? (n.type === 'd' || (n.mode & 0o111) ? 1 : 0) : 0;
            [['u', 6], ['g', 3], ['o', 0]].forEach(([w, sh]) => {
              if (!(who.includes(w) || who.includes('a'))) return;
              if (p === 'r') bits |= 4 << sh; if (p === 'w') bits |= 2 << sh; if (p === 'x' || x) bits |= 1 << sh;
            });
            if (p === 's') { if (who.includes('u') || who.includes('a')) bits |= 0o4000; if (who.includes('g') || who.includes('a')) bits |= 0o2000; }
            if (p === 't') bits |= 0o1000;
          });
          if (!m[1] && op !== '=') bits &= ~this.umask | 0o7000;
          const mask = ['u', 'g', 'o'].reduce((s, w, i) => who.includes(w) || who.includes('a') ? s | (7 << (6 - i * 3)) : s, 0);
          n.mode = op === '+' ? n.mode | bits : op === '-' ? n.mode & ~bits : (n.mode & ~mask) | bits;
        }
      }
      n.mtime = n.mtime;
      if (f.v) this.out(`mode of '${t}' changed to ${n.mode.toString(8).padStart(4, '0')} (${modeStr(n).slice(1)})\n`);
    };
    args.forEach(t => {
      const n = this.node(this.abs(t));
      if (!n) { this.eout(`chmod: cannot access '${t}': No such file or directory\n`); code = 1; return; }
      const walk = (m, path) => { apply(m, path); if (f.R && m.type === 'd') Object.entries(m.kids).forEach(([k, v]) => walk(v, path + '/' + k)); };
      walk(n, t);
    });
    return code;
  };
  C.chown = function (a) {
    const [f, rest] = opts(a);
    if (rest.length < 2) { this.eout('chown: missing operand\n'); return 1; }
    const [own, grp] = rest.shift().split(':');
    if (own && !(own in UIDS)) { this.eout(`chown: invalid user: '${own}'\n`); return 1; }
    let code = 0;
    rest.forEach(t => {
      const n = this.node(this.abs(t));
      if (!n) { this.eout(`chown: cannot access '${t}': No such file or directory\n`); code = 1; return; }
      const mine = this.user === 'learner' ? ['learner', 'sudo'] : [this.user];
      const okGroupOnly = !own && grp && n.owner === this.user && mine.includes(grp);
      if (grp && !(grp in UIDS) && grp !== 'sudo' && grp !== 'www-data') { this.eout(`${this.cmdName || 'chown'}: invalid group: '${grp}'\n`); code = 1; return; }
      if (this.user !== 'root' && !okGroupOnly) { this.eout(own ? `chown: changing ownership of '${t}': Operation not permitted\n` : `chgrp: changing group of '${t}': Operation not permitted\n`); code = 1; return; }
      const walk = m => { if (own) m.owner = own; if (grp !== undefined) m.group = grp || own; if (f.R && m.type === 'd') Object.values(m.kids).forEach(walk); };
      walk(n);
    });
    return code;
  };
  C.chgrp = function (a) { this.cmdName = 'chgrp'; try { return C.chown.call(this, [':' + a[0]].concat(a.slice(1))); } finally { this.cmdName = ''; } };
  C.whoami = function () { this.out(this.user + '\n'); };
  C.id = function (a) {
    const u = a[0] || this.user, uid = UIDS[u];
    if (uid === undefined) { this.eout(`id: '${u}': no such user\n`); return 1; }
    const extra = u === 'learner' ? ',27(sudo)' : '';
    this.out(`uid=${uid}(${u}) gid=${uid}(${u}) groups=${uid}(${u})${extra}\n`);
  };
  C.groups = function () { this.out(this.user === 'learner' ? 'learner sudo\n' : this.user + '\n'); };
  C.hostname = function () { this.out(HOST + '\n'); };
  C.uname = function (a) {
    const [f] = opts(a);
    if (f.a) this.out(`Linux ${HOST} 6.8.0-practice #1 SMP x86_64 GNU/Linux\n`);
    else this.out([f.s || (!f.r && !f.m && !f.n) ? 'Linux' : '', f.n ? HOST : '', f.r ? '6.8.0-practice' : '', f.m ? 'x86_64' : ''].filter(Boolean).join(' ') + '\n');
  };
  C.date = function (a) {
    const d = new Date();
    if (a[0] && a[0].startsWith('+')) {
      const z = n => String(n).padStart(2, '0');
      this.out(a[0].slice(1).replace(/%([YmdHMSjAaBbs%F T])/g, (_, c) => ({ Y: d.getFullYear(), m: z(d.getMonth() + 1), d: z(d.getDate()), H: z(d.getHours()), M: z(d.getMinutes()), S: z(d.getSeconds()), F: `${d.getFullYear()}-${z(d.getMonth() + 1)}-${z(d.getDate())}`, T: `${z(d.getHours())}:${z(d.getMinutes())}:${z(d.getSeconds())}`, A: d.toLocaleDateString('en-GB', { weekday: 'long' }), a: d.toLocaleDateString('en-GB', { weekday: 'short' }), B: d.toLocaleDateString('en-GB', { month: 'long' }), b: d.toLocaleDateString('en-GB', { month: 'short' }), s: Math.floor(d / 1000), '%': '%' }[c] ?? c)) + '\n');
    } else this.out(d.toString().replace(/ GMT.*$/, '') + '\n');
  };
  C.cal = function () { this.out('   November 2026\nSu Mo Tu We Th Fr Sa\n 1  2  3  4  5  6  7\n 8  9 10 11 12 13 14\n15 16 17 18 19 20 21\n22 23 24 25 26 27 28\n29 30\n'); };
  C.uptime = function () { this.out(' 10:15:02 up 3 days,  2:41,  1 user,  load average: 0.42, 0.35, 0.30\n'); };
  C.free = function (a) {
    const [f] = opts(a);
    this.out(f.h ? '               total        used        free      shared  buff/cache   available\nMem:           7.7Gi       2.1Gi       3.0Gi       120Mi       2.6Gi       5.3Gi\nSwap:          2.0Gi          0B       2.0Gi\n'
      : '               total        used        free      shared  buff/cache   available\nMem:         8048304     2201124     3142212      122880     2704968     5563880\nSwap:        2097148           0     2097148\n');
  };
  C.df = function (a) {
    const [f] = opts(a);
    this.out(f.h ? 'Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        40G   15G   23G  40% /\ntmpfs           3.9G     0  3.9G   0% /dev/shm\n'
      : 'Filesystem     1K-blocks     Used Available Use% Mounted on\n/dev/sda1       41152736 15204920  23834288  39% /\ntmpfs            4024152        0   4024152   0% /dev/shm\n');
  };
  C.du = function (a) {
    const [f, rest] = opts(a, 'd');
    const targets = rest.length ? rest : ['.'];
    const size = n => n.type === 'd' ? 4 + Object.values(n.kids).reduce((s, k) => s + size(k), 0) : n.type === 'f' && this.size(n) ? Math.ceil(this.size(n) / 4096) * 4 : 0;
    targets.forEach(t => {
      const n = this.node(this.abs(t));
      if (!n) { this.eout(`du: cannot access '${t}': No such file or directory\n`); return; }
      const show = (m, p, depth) => {
        if (m.type === 'd' && !f.s) Object.entries(m.kids).sort().forEach(([k, v]) => { if (v.type === 'd') show(v, p.replace(/\/$/, '') + '/' + k, depth + 1); else if (f.a) this.out(`${f.h ? human(size(v) * 1024) : size(v)}\t${p.replace(/\/$/, '')}/${k}\n`); });
        if (f.d !== undefined && depth > +f.d) return;
        this.out(`${f.h ? human(size(m) * 1024) : size(m)}\t${p}\n`);
      };
      show(n, t, 0);
    });
  };
  C.history = function (a) {
    if (a[0] === '-c') { this.hist = []; return 0; }
    this.hist.forEach((h, i) => this.out(`${pad(i + 1, 5)}  ${h}\n`));
  };
  C.clear = function () { this.cleared = true; };
  C.man = function (a) {
    if (!a.length) { this.out('What manual page do you want?\nFor example, try \'man man\'.\n'); return 1; }
    const c = a[a.length - 1];
    if (c === 'man') { this.out('man [SECTION] PAGE  show a manual page. Sections: 1 user commands, 2 system calls, 3 library functions, 4 devices, 5 file formats, 6 games, 7 overviews, 8 admin commands. In a real terminal press q to quit and /word to search.\n'); return 0; }
    if (MAN[c]) { this.out(`${c.toUpperCase()}(1)\n\n${MAN[c]}\n\n(The practice shell shows a short summary. On a real Linux system man ${c} opens the full manual.)\n`); return 0; }
    if (C[c]) { this.out(`${c}: a command of this practice shell. On a real Linux system man ${c} opens its full manual.\n`); return 0; }
    this.eout(`No manual entry for ${c}\n`); return 16;
  };
  C.help = function () {
    this.out('This practice shell understands:\n' + Object.keys(C).filter(k => !['egrep', 'more', '[', 'sh', '.', 'logout'].includes(k)).sort().join(' ').replace(/(.{1,72})(\s|$)/g, '$1\n') + 'Also pipes |, redirections > >> < 2> 2>&1, && || ;, variables, $(command), $((1 + 2)), globs * ? [abc], braces {a,b} {1..5}, for, while, until, if, case and functions.\nType man followed by a command name for a short summary.\n');
  };
  C.type = function (a) {
    let code = 0;
    a.forEach(c => {
      if (this.aliases[c]) this.out(`${c} is aliased to \`${this.aliases[c]}'\n`);
      else if (this.fns && this.fns[c]) this.out(`${c} is a function\n`);
      else if (['if', 'then', 'else', 'fi', 'for', 'while', 'do', 'done', 'case', 'esac', 'until'].includes(c)) this.out(`${c} is a shell keyword\n`);
      else if (BUILTIN.has(c)) this.out(`${c} is a shell builtin\n`);
      else if (this.lookup(c)) this.out(`${c} is ${this.lookup(c).path}\n`);
      else if (C[c] && !CMDS.includes(c)) this.out(`${c} is /usr/bin/${c}\n`);
      else { this.eout(`bash: type: ${c}: not found\n`); code = 1; }
    });
    return code;
  };
  C.which = function (a) { let code = 0; a.filter(c => !c.startsWith('-')).forEach(c => { const h = this.lookup(c); if (h) this.out(h.path + '\n'); else code = 1; }); return code; };
  C.file = function (a) {
    a.forEach(t => {
      const n = this.node(this.abs(t), false);
      if (!n) { this.out(`${t}: cannot open \`${t}' (No such file or directory)\n`); return; }
      const pk = n.type === 'f' && this.unpack(n.data), PKD = { tar: 'POSIX tar archive (GNU)', gz: 'gzip compressed data, from Unix', xz: 'XZ compressed data, checksum CRC64', bz2: 'bzip2 compressed data, block size = 900k', zip: 'Zip archive data, at least v1.0 to extract' };
      const what = pk ? (pk.kind === 'gz' && pk.name ? `gzip compressed data, was "${pk.name}", from Unix` : PKD[pk.kind]) : n.type === 'd' ? 'directory' : n.type === 'l' ? `symbolic link to ${n.target}` : n.type === 'c' ? 'character special (1/3)' : /^#!practice/.test(n.data) ? 'ELF 64-bit LSB pie executable, x86-64' : /^#!.*bash/.test(n.data) ? 'Bourne-Again shell script, ASCII text executable' : n.data === 'JPEGDATA' ? 'JPEG image data' : n.data === 'PNGDATA' ? 'PNG image data' : !n.data ? 'empty' : /\.csv$/.test(t) ? 'CSV ASCII text' : /^</.test(n.data) ? 'HTML document, ASCII text' : 'ASCII text';
      this.out(`${t}: ${what}\n`);
    });
  };
  C.stat = function (a) {
    const [f, rest] = opts(a, 'c');
    rest.forEach(t => {
      const n = this.node(this.abs(t), false);
      if (!n) { this.eout(`stat: cannot statx '${t}': No such file or directory\n`); this.err = true; return; }
      if (f.c) {
        const typ = n.type === 'd' ? 'directory' : n.type === 'l' ? 'symbolic link' : this.size(n) ? 'regular file' : 'regular empty file';
        const map = { a: n.mode.toString(8), A: modeStr(n), n: t, U: n.owner, G: n.group, u: String(UIDS[n.owner] ?? 1000), g: String(UIDS[n.group] ?? 1000), s: String(this.size(n)), F: typ, '%': '%' };
        this.out(String(f.c).replace(/%(.)/g, (m, k) => map[k] ?? m) + '\n');
        return;
      }
      const ty = n.type === 'd' ? 'directory' : n.type === 'l' ? 'symbolic link' : n.type === 'c' ? 'character special file' : this.size(n) ? 'regular file' : 'regular empty file';
      const dt = new Date(n.mtime).toISOString().replace('T', ' ').replace(/\.\d+Z/, '.000000000 +0000');
      this.out(`  File: ${t}${n.type === 'l' ? ' -> ' + n.target : ''}\n  Size: ${this.size(n)}\t\tBlocks: ${n.type === 'd' ? 8 : this.size(n) ? 8 : 0}\tIO Block: 4096   ${ty}\nAccess: (${n.mode.toString(8).padStart(4, '0')}/${modeStr(n)})  Uid: (${pad(UIDS[n.owner] ?? 1000, 5)}/${pad(n.owner, 8)})   Gid: (${pad(UIDS[n.group] ?? 1000, 5)}/${pad(n.group, 8)})\nModify: ${dt}\n`);
    });
    return this.err ? 1 : 0;
  };
  C.ln = function (a) {
    const [f, rest] = opts(a);
    if (rest.length < 2) { this.eout('ln: missing file operand\n'); return 1; }
    const [tgt, link] = rest, lp = this.abs(link), ln = this.node(lp);
    const to = ln && ln.type === 'd' ? lp + '/' + baseName(tgt) : lp;
    if (this.node(to, false)) { if (!f.f) { this.eout(`ln: failed to create ${f.s ? 'symbolic' : 'hard'} link '${link}': File exists\n`); return 1; } this.removeNode(to); }
    if (f.s) { this.mk(to, 'l', 0o777, this.user, tgt).mtime = this.now(); return 0; }
    const src = this.node(this.abs(tgt));
    if (!src) { this.eout(`ln: failed to access '${tgt}': No such file or directory\n`); return 1; }
    if (src.type === 'd') { this.eout(`ln: ${tgt}: hard link not allowed for directory\n`); return 1; }
    this.node(dirName(to)).kids[baseName(to)] = src;   /* the same node under a second name, just like a hard link */
  };
  C.readlink = function (a) { const [f, rest] = opts(a); const n = this.node(this.abs(rest[0]), false); if (f.f) { this.out(this.abs(rest[0]) + '\n'); return 0; } if (!n || n.type !== 'l') return 1; this.out(n.target + '\n'); };
  C.find = function (a) {
    let i = 0; const starts = [];
    while (a[i] !== undefined && !/^-./.test(a[i]) && a[i] !== '!' && a[i] !== '(') starts.push(a[i++]);
    if (!starts.length) starts.push('.');
    let maxd = Infinity, mind = 0, hasAction = false, delAll = false;
    const plusRuns = [], toDelete = [];
    const self = this;
    /* expression grammar: or := and (-o and)*, and := not ((-a)? not)*, not := (! | -not)* prim, prim := ( or ) | test | action */
    const toks = a.slice(i);
    let k = 0;
    const need = o => { if (toks[k] === undefined) throw new Error(`missing argument to \`${o}'`); return toks[k++]; };
    const parseOr = () => { let l = parseAnd(); while (toks[k] === '-o' || toks[k] === '-or') { k++; const r = parseAnd(); const L = l; l = c => L(c) || r(c); } return l; };
    const parseAnd = () => { let l = parseNot(); while (k < toks.length && toks[k] !== '-o' && toks[k] !== '-or' && toks[k] !== ')') { if (toks[k] === '-a' || toks[k] === '-and') k++; const r = parseNot(); const L = l; l = c => L(c) && r(c); } return l; };
    const parseNot = () => { if (toks[k] === '!' || toks[k] === '-not') { k++; const e = parseNot(); return c => !e(c); } return prim(); };
    const cmpNum = (spec, val) => { const m = /^([+-]?)(\d+)$/.exec(spec); if (!m) throw new Error(`invalid argument \`${spec}'`); return m[1] === '+' ? val > +m[2] : m[1] === '-' ? val < +m[2] : val === +m[2]; };
    const prim = () => {
      const o = toks[k++];
      if (o === '(') { const e = parseOr(); if (toks[k++] !== ')') throw new Error("invalid expression; I was expecting to find a ')' somewhere but did not see one."); return e; }
      if (o === '-name' || o === '-iname') { const re = new RegExp(globRe(need(o)).source, o === '-iname' ? 'i' : ''); return c => re.test(c.name); }
      if (o === '-path' || o === '-wholename' || o === '-ipath') { const g = need(o); const re = new RegExp('^' + g.split('*').map(x => x.replace(/[.+^${}()|[\]\\?]/g, '\\$&')).join('.*').replace(/\\\?/g, '.') + '$', o === '-ipath' ? 'i' : ''); return c => re.test(c.path); }
      if (o === '-type') { const v = need(o); return c => v.split(',').includes(c.n.type); }
      if (o === '-maxdepth') { maxd = +need(o); return () => true; }
      if (o === '-mindepth') { mind = +need(o); return () => true; }
      if (o === '-empty') return c => (c.n.type === 'd' ? !Object.keys(c.n.kids).length : c.n.type === 'f' && self.size(c.n) === 0);
      if (o === '-size') { const v = need(o), m = /^([+-]?)(\d+)([bckwMG]?)$/.exec(v); if (!m) throw new Error(`invalid -size type in \`${v}'`); const unit = { c: 1, w: 2, k: 1024, M: 1048576, G: 1073741824, b: 512, '': 512 }[m[3]]; return c => cmpNum(m[1] + m[2], Math.ceil(self.size(c.n) / unit)); }
      if (o === '-newer') { const r = self.node(self.abs(need(o))); return c => !!r && c.n.mtime > r.mtime; }
      if (o === '-mmin' || o === '-mtime') { const v = need(o), per = o === '-mmin' ? 60000 : 86400000; return c => cmpNum(v, Math.floor((self.clock - c.n.mtime) / per)); }
      if (o === '-perm') { const v = need(o); let want; if (/^[-/]?[0-7]+$/.test(v)) want = parseInt(v.replace(/^[-/]/, ''), 8); else { want = 0; v.replace(/^[-/]/, '').split(',').forEach(cl => { const m = /^([ugoa]*)[+=]([rwxst]*)$/.exec(cl); if (!m) return; const who = m[1] || 'a'; [...m[2]].forEach(p => [['u', 6], ['g', 3], ['o', 0]].forEach(([w, sh]) => { if (who.includes(w) || who.includes('a')) want |= ({ r: 4, w: 2, x: 1 }[p] || 0) << sh; })); }); } return c => v[0] === '-' ? (c.n.mode & want) === want : v[0] === '/' ? (c.n.mode & want) !== 0 : (c.n.mode & 0o7777) === want; }
      if (o === '-user') { const v = need(o); return c => c.n.owner === v; }
      if (o === '-group') { const v = need(o); return c => c.n.group === v; }
      if (o === '-readable' || o === '-writable' || o === '-executable') { const w = { '-readable': 'r', '-writable': 'w', '-executable': 'x' }[o]; return c => self.can(c.n, w); }
      if (o === '-true') return () => true;
      if (o === '-false') return () => false;
      if (o === '-print' || o === '-print0') { hasAction = true; return c => { self.out(c.path + (o === '-print0' ? '\u0000' : '\n')); return true; }; }
      if (o === '-ls') { hasAction = true; return c => { self.out(`${String(c.n.ino || 0).padStart(7)} ${self.size(c.n) > 0 ? 4 : 0} ${modeStr(c.n)} 1 ${c.n.owner} ${c.n.group} ${String(self.size(c.n)).padStart(6)} ${c.path}\n`); return true; }; }
      if (o === '-prune') return c => { c.prune = true; return true; };
      if (o === '-delete') { hasAction = true; delAll = true; return c => { toDelete.push(c.path); return true; }; }
      if (o === '-exec' || o === '-ok') {
        hasAction = true;
        const cmd = []; while (k < toks.length && toks[k] !== ';' && !(toks[k] === '+' && toks[k - 1] === '{}')) cmd.push(toks[k++]);
        if (k >= toks.length) throw new Error("missing argument to `-exec'");
        if (toks[k++] === '+') { const run = { cmd, paths: [] }; plusRuns.push(run); return c => { run.paths.push(c.path); return true; }; }
        return c => self.call(cmd.map(x => x.split('{}').join(c.path)), '') === 0;
      }
      throw new Error(o === undefined ? 'expected an expression' : `unknown predicate \`${o}'`);
    };
    let expr;
    try { expr = toks.length ? parseOr() : () => true; if (k < toks.length) throw new Error(`paths must precede expression: \`${toks[k]}'`); } catch (e) { this.eout(`find: ${e.message}\n`); return 1; }
    starts.forEach(st => {
      const root = this.node(this.abs(st));
      if (!root) { this.eout(`find: '${st}': No such file or directory\n`); this.err = true; return; }
      const walk = (n, p, d) => {
        const c = { n, name: d === 0 ? (st === '/' ? '/' : baseName(st.replace(/\/+$/, '')) || st) : n.name, path: p, prune: false };
        if (d >= mind && d <= maxd) { const ok = expr(c); if (ok && !hasAction) this.out(p + '\n'); }
        if (n.type === 'd' && d < maxd && !c.prune) {
          if (!this.can(n, 'r') || !this.can(n, 'x')) { this.eout(`find: '${p}': Permission denied\n`); this.err = true; return; }
          Object.keys(n.kids).sort().forEach(kk => walk(n.kids[kk], p.replace(/\/$/, '') + '/' + kk, d + 1));
        }
      };
      walk(root, st, 0);
    });
    plusRuns.forEach(r => { if (r.paths.length) this.call(r.cmd.flatMap(x => x === '{}' ? r.paths : [x]), ''); });
    if (delAll) toDelete.reverse().forEach(p => { const n = this.node(this.abs(p), false); if (!n) return; if (n.type === 'd' && Object.keys(n.kids).length) { this.eout(`find: cannot delete '${p}': Directory not empty\n`); this.err = true; return; } this.removeNode(this.abs(p)); });
    return this.err ? 1 : 0;
  };
  /* ---------- archives and compression: tar, gzip, xz, bzip2, zip ----------
     A packed file holds a short marker string, and the real contents live in this.packs, so a packed file can be
     copied, moved, piped and redirected like any other file. Sizes of compressed files are estimates. */
  const PKRE = /^\u0000PK(\d+)\u0000$/;
  const ZK = { gz: { ext: '.gz', cmd: 'gzip', name: 'gzip' }, xz: { ext: '.xz', cmd: 'xz', name: 'xz' }, bz2: { ext: '.bz2', cmd: 'bzip2', name: 'bzip2' } };
  const isoTime = ms => new Date(ms).toISOString().slice(0, 16).replace('T', ' ');
  World.prototype.pack = function (p) { this.packs = this.packs || []; this.packs.push(p); return '\u0000PK' + (this.packs.length - 1) + '\u0000'; };
  World.prototype.unpack = function (s) { const m = PKRE.exec(s || ''); return m && this.packs ? this.packs[+m[1]] : null; };
  /* how many bytes of real information a string holds: tar padding and headers squeeze down to almost nothing */
  World.prototype.info = function (s) { const p = this.unpack(s); if (!p) return enc(s || ''); if (p.kind === 'tar' || p.kind === 'zip') return p.items.reduce((t, x) => t + 40 + (x.data ? this.info(x.data) : 0), 0); return p.size; };
  World.prototype.squeeze = function (kind, data, name) {
    const el = this.info(data);
    const body = el < 64 ? el + 2 : Math.ceil(el * 0.4) + 30;
    const size = kind === 'gz' ? 18 + (name ? enc(name) + 1 : 0) + body : kind === 'xz' ? Math.ceil((60 + el * 0.42) / 4) * 4 : 40 + Math.ceil(el * 0.45);
    return this.pack({ kind, name, inner: data, size, usize: this.unpack(data) ? this.unpack(data).size : enc(data) });
  };
  /* turn a folder tree into archive items, in sorted order */
  World.prototype.collect = function (path, member, items, skip) {
    const n = this.node(path, false);
    if (!n) return false;
    if (skip(member)) return true;
    if (n.type === 'd') {
      items.push({ path: member.replace(/\/*$/, '/'), type: 'd', mode: n.mode, owner: n.owner, group: n.group, mtime: n.mtime });
      if (!this.can(n, 'r') || !this.can(n, 'x')) { this.eout(`${this.cmdName || 'tar'}: ${member}: Cannot open: Permission denied\n`); this.err = true; return true; }
      Object.keys(n.kids).sort().forEach(k => this.collect(path + '/' + k, member.replace(/\/*$/, '/') + k, items, skip));
    } else if (n.type === 'l') items.push({ path: member, type: 'l', mode: 0o777, owner: n.owner, group: n.group, mtime: n.mtime, target: n.target });
    else {
      if (!this.can(n, 'r')) { this.eout(`${this.cmdName || 'tar'}: ${member}: Cannot open: Permission denied\n`); this.err = true; return true; }
      items.push({ path: member, type: 'f', mode: n.mode, owner: n.owner, group: n.group, mtime: n.mtime, data: n.data });
    }
    return true;
  };
  /* write archive items under a folder. Returns false when a step was refused */
  World.prototype.lay = function (base, it, keepOld) {
    const p = norm(base + '/' + it.path);
    const parent = dirName(p);
    if (!this.node(parent)) this.mkdirs(parent);
    const dir = this.node(parent);
    if (!dir || dir.type !== 'd' || !this.can(dir, 'w')) return 'Cannot open: Permission denied';
    const old = this.node(p, false);
    if (it.type === 'd') { if (!old) this.mk(p, 'd', it.mode & ~this.umask & 0o7777, this.user).mtime = it.mtime; return ''; }
    if (old && keepOld) return 'Cannot open: File exists';
    if (old && old.type === 'd') return 'Cannot open: Is a directory';
    const n = this.mk(p, it.type, it.type === 'l' ? 0o777 : it.mode & ~this.umask & 0o7777, this.user, it.type === 'l' ? it.target : it.data);
    n.mtime = it.mtime;
    return '';
  };

  C.tar = function (a0, input) {
    const a = a0.slice();
    if (a[0] && !a[0].startsWith('-')) a[0] = '-' + a[0];
    let mode = '', file = null, dir = null, z = '', v = 0, auto = false, keep = false, strip = 0;
    const ex = [], names = [];
    for (let i = 0; i < a.length; i++) {
      const x = a[i];
      if (x.startsWith('--')) {
        const [k, val] = x.slice(2).split(/=(.*)/s);
        const need = () => val !== undefined ? val : a[++i];
        if (k === 'create') mode = 'c'; else if (k === 'extract' || k === 'get') mode = 'x'; else if (k === 'list') mode = 't'; else if (k === 'append') mode = 'r';
        else if (k === 'file') file = need(); else if (k === 'directory') dir = need(); else if (k === 'exclude') ex.push(need());
        else if (k === 'gzip' || k === 'gunzip') z = 'gz'; else if (k === 'xz') z = 'xz'; else if (k === 'bzip2') z = 'bz2';
        else if (k === 'verbose') v++; else if (k === 'auto-compress') auto = true; else if (k === 'keep-old-files') keep = true;
        else if (k === 'strip-components') strip = +need();
        else if (k === 'sort') need();
        else { this.eout(`tar: unrecognized option '${x}'\nTry 'tar --help' or 'tar --usage' for more information.\n`); return 2; }
        continue;
      }
      if (x.startsWith('-') && x.length > 1) {
        for (let j = 1; j < x.length; j++) {
          const ch = x[j];
          if ('ctxr'.includes(ch)) mode = ch; else if (ch === 'v') v++; else if (ch === 'z') z = 'gz'; else if (ch === 'J') z = 'xz'; else if (ch === 'j') z = 'bz2';
          else if (ch === 'a') auto = true; else if (ch === 'k') keep = true;
          else if (ch === 'f' || ch === 'C') { const val = x.slice(j + 1) || a[++i]; if (ch === 'f') file = val; else dir = val; break; }
          else { this.eout(`tar: invalid option -- '${ch}'\nTry 'tar --help' or 'tar --usage' for more information.\n`); return 2; }
        }
        continue;
      }
      names.push(x);
    }
    const fatal = m => { this.eout(`tar: ${m}\ntar: Error is not recoverable: exiting now\n`); return 2; };
    if (!mode) { this.eout("tar: You must specify one of the '-Acdtrux', '--delete' or '--test-label' options\nTry 'tar --help' or 'tar --usage' for more information.\n"); return 2; }
    const base = dir ? this.abs(dir) : this.cwd;
    if (dir && (!this.node(base) || this.node(base).type !== 'd')) return fatal(`${dir}: Cannot open: No such file or directory`);
    if (mode === 'c' || mode === 'r') {
      if (!names.length) return fatal('Cowardly refusing to create an empty archive');
      if (!file) return fatal('Refusing to write archive contents to terminal (missing -f option?)');
      if (auto && !z) z = /\.(tgz|tar\.gz)$/.test(file) ? 'gz' : /\.(txz|tar\.xz)$/.test(file) ? 'xz' : /\.(tbz2?|tar\.bz2)$/.test(file) ? 'bz2' : '';
      let items = [];
      if (mode === 'r') { const an = this.node(this.abs(file)); const p = an && this.unpack(an.data); if (p && p.kind !== 'tar') return fatal('Cannot update compressed archives'); if (p) items = p.items.slice(); }
      const skip = m => ex.some(g => globRe(g).test(baseName(m)) || globRe(g).test(m.replace(/\/$/, '')));
      let warned = false, code = 0;
      names.forEach(nm => {
        let member = nm;
        if (member.startsWith('/')) { member = member.replace(/^\/+/, ''); if (!warned) { this.eout("tar: Removing leading `/' from member names\n"); warned = true; } }
        const start = items.length;
        if (!this.collect(nm.startsWith('/') ? nm : base + '/' + nm, member || '.', items, skip)) { this.eout(`tar: ${nm}: Cannot stat: No such file or directory\n`); code = 2; return; }
        if (v) items.slice(start).forEach(it => this.out(v > 1 ? this.tarLine(it) : it.path + '\n'));
      });
      if (this.err) code = 2;
      let data = this.pack({ kind: 'tar', items, size: Math.ceil((items.reduce((t, x) => t + 512 + (x.data ? Math.ceil(enc(x.data) / 512) * 512 : 0), 0) + 1024) / 10240) * 10240 });
      if (z) data = this.squeeze(z, data, '');
      if (file === '-') { this.out(data); if (code) this.eout('tar: Exiting with failure status due to previous errors\n'); return code; }
      const fp = this.abs(file), parent = this.node(dirName(fp));
      if (!parent) return fatal(`${file}: Cannot open: No such file or directory`);
      const old = this.node(fp);
      if (old && !this.can(old, 'w') || !old && !this.can(parent, 'w')) return fatal(`${file}: Cannot open: Permission denied`);
      if (old) { old.data = data; old.mtime = this.now(); } else this.mk(fp, 'f', 0o666 & ~this.umask, this.user, data).mtime = this.now();
      if (code) this.eout('tar: Exiting with failure status due to previous errors\n');
      return code;
    }
    if (!file) return fatal('Refusing to read archive contents from terminal (missing -f option?)');
    const an = file === '-' ? { type: 'f', data: input, mode: 0o644, owner: this.user } : this.node(this.abs(file));
    if (!an) return fatal(`${file}: Cannot open: No such file or directory`);
    if (an.type === 'd') return fatal(`${file}: Read error at byte 0, while reading 10240 bytes: Is a directory`);
    if (!this.can(an, 'r')) return fatal(`${file}: Cannot open: Permission denied`);
    let p = this.unpack(an.data);
    while (p && ZK[p.kind]) p = this.unpack(p.inner);
    if (!p || p.kind !== 'tar') { this.eout('tar: This does not look like a tar archive\ntar: Exiting with failure status due to previous errors\n'); return 2; }
    const wanted = it => !names.length || names.some(nm => { const n = nm.replace(/\/+$/, ''); return it.path.replace(/\/$/, '') === n || it.path.startsWith(n + '/'); });
    let code = 0;
    const hit = new Set();
    p.items.forEach(it => {
      if (!wanted(it)) return;
      names.forEach(nm => { const n = nm.replace(/\/+$/, ''); if (it.path.replace(/\/$/, '') === n || it.path.startsWith(n + '/')) hit.add(nm); });
      if (mode === 't') { this.out(v ? this.tarLine(it) : it.path + '\n'); return; }
      const parts = it.path.split('/').filter(Boolean);
      if (parts.length <= strip) return;
      const rel = Object.assign({}, it, { path: parts.slice(strip).join('/') + (it.type === 'd' ? '/' : '') });
      if (v) this.out(v > 1 ? this.tarLine(it) : it.path + '\n');
      const why = this.lay(base, rel, keep);
      if (why) { this.eout(`tar: ${rel.path}: ${why}\n`); code = 2; }
    });
    names.filter(n => !hit.has(n)).forEach(n => { this.eout(`tar: ${n}: Not found in archive\n`); code = 2; });
    if (code) this.eout('tar: Exiting with failure status due to previous errors\n');
    return code;
  };
  World.prototype.tarLine = function (it) {
    const ug = `${it.owner}/${it.group}`, sz = String(it.data ? enc(it.data) : 0);
    const m = modeStr({ type: it.type, mode: it.mode });
    return `${m} ${ug}${pad(sz, Math.max(19 - ug.length, sz.length + 1))} ${isoTime(it.mtime)} ${it.path}${it.type === 'l' ? ' -> ' + it.target : ''}\n`;
  };

  /* gzip, xz and bzip2 share one engine */
  function squeezer(kind, defaults) {
    return function (a, input) {
      const K = ZK[kind], me = this.cmdLabel || K.cmd;
      const [f0, rest] = opts(a);
      const f = Object.assign({}, defaults, f0);
      const dec = f.d || f['--decompress'] || f['--uncompress'], toOut = f.c || f['--stdout'], keepIn = f.k || f['--keep'] || toOut, force = f.f || f['--force'];
      if (!rest.length) {
        if (!dec) { this.out(this.squeeze(kind, input, '')); return 0; }
        const p = this.unpack(input);
        if (!p || p.kind !== kind) { this.eout(kind === 'gz' ? 'gzip: stdin: not in gzip format\n' : kind === 'xz' ? `${me}: (stdin): File format not recognized\n` : `${me}: (stdin) is not a bzip2 file.\n`); return 1; }
        this.out(p.inner); return 0;
      }
      let code = 0;
      const one = (t, recursed) => {
        const fp = this.abs(t), n = this.node(fp, false);
        if (!n) { this.eout(kind === 'xz' ? `${me}: ${t}: No such file or directory\n` : `${me}: ${t}: No such file or directory\n`); code = Math.max(code, 1); return; }
        if (n.type === 'd') {
          if (f.r && kind === 'gz') { Object.keys(n.kids).sort().forEach(k => one(t.replace(/\/$/, '') + '/' + k, true)); return; }
          this.eout(kind === 'gz' ? `gzip: ${t} is a directory -- ignored\n` : kind === 'xz' ? `${me}: ${t}: Is a directory, skipping\n` : `${me}: Input file ${t} is a directory.\n`); code = 2; return;
        }
        if (f.l && kind === 'gz') {
          const p = this.unpack(n.data);
          if (!p || p.kind !== 'gz') { this.eout(`gzip: ${t}: not in gzip format\n`); code = 1; return; }
          if (!this.listedHead) { this.out('         compressed        uncompressed  ratio uncompressed_name\n'); this.listedHead = true; }
          this.out(`${pad(p.size, 19)} ${pad(p.usize, 19)} ${pad(((1 - p.size / Math.max(p.usize, 1)) * 100).toFixed(1), 5)}% ${t.replace(/\.gz$/, '')}\n`);
          return;
        }
        if (!this.can(n, 'r')) { this.eout(`${me}: ${t}: Permission denied\n`); code = 1; return; }
        if (f.t || f['--test']) { const p = this.unpack(n.data); if (!p || p.kind !== kind) { this.eout(kind === 'gz' ? `gzip: ${t}: not in gzip format\n` : `${me}: ${t}: File format not recognized\n`); code = 1; } return; }
        if (dec) {
          const p = this.unpack(n.data);
          const outName = t.endsWith(K.ext) ? t.slice(0, -K.ext.length) : kind === 'gz' && t.endsWith('.tgz') ? t.slice(0, -4) + '.tar' : null;
          if (!outName && !toOut) { this.eout(kind === 'gz' ? `gzip: ${t}: unknown suffix -- ignored\n` : `${me}: ${t}: Filename has an unknown suffix, skipping\n`); code = Math.max(code, 2); return; }
          if (!p || p.kind !== kind) { this.eout(kind === 'gz' ? `gzip: ${t}: not in gzip format\n` : kind === 'xz' ? `${me}: ${t}: File format not recognized\n` : `${me}: ${t} is not a bzip2 file.\n`); code = 1; return; }
          if (toOut) { this.out(p.inner); return; }
          { const r = this.swap(n, fp, this.abs(outName), p.inner, t, outName, keepIn, force, kind, me, f.v, p); if (r) code = Math.max(code, r); return; }
        }
        if (t.endsWith(K.ext) || kind === 'gz' && t.endsWith('.tgz')) {
          if (recursed) return;
          this.eout(kind === 'gz' ? `gzip: ${t} already has ${K.ext} suffix -- unchanged\n` : `${me}: ${t}: File already has \`${K.ext}' suffix, skipping\n`); code = Math.max(code, 2); return;
        }
        const packed = this.squeeze(kind, n.data, kind === 'gz' ? baseName(t) : '');
        if (toOut) { this.out(packed); return; }
        const r = this.swap(n, fp, fp + K.ext, packed, t, t + K.ext, keepIn, force, kind, me, f.v, this.unpack(packed));
        if (r) code = Math.max(code, r);
      };
      rest.forEach(t => one(t, false));
      this.listedHead = false;
      return code;
    };
  }
  /* write the new file next to the old one, then remove the old one unless asked to keep it */
  World.prototype.swap = function (n, from, to, data, fromName, toName, keepIn, force, kind, me, verbose, p) {
    const parent = this.node(dirName(to));
    if (this.node(to, false) && !force) {
      this.eout(kind === 'gz' ? `gzip: ${toName} already exists;\tnot overwritten\n` : `${me}: ${toName}: File exists\n`);
      return kind === 'gz' ? 2 : 1;
    }
    if (!this.can(parent, 'w')) { this.eout(`${me}: ${toName}: Permission denied\n`); return 1; }
    const made = this.mk(to, 'f', n.mode, n.owner, data);
    made.group = n.group; made.mtime = n.mtime;
    if (!keepIn) this.removeNode(from);
    if (verbose && kind === 'gz') this.out(`${fromName}:\t${pad(((1 - p.size / Math.max(p.usize, 1)) * 100).toFixed(1), 5)}% -- ${keepIn ? 'created' : 'replaced with'} ${toName}\n`);
    return 0;
  };
  C.gzip = squeezer('gz', {});
  C.gunzip = function (a, i) { this.cmdLabel = 'gzip'; try { return C.gzip.call(this, ['-d'].concat(a), i); } finally { this.cmdLabel = ''; } };
  C.zcat = function (a, i) { this.cmdLabel = 'gzip'; try { return C.gzip.call(this, ['-d', '-c'].concat(a), i); } finally { this.cmdLabel = ''; } };
  C.xz = squeezer('xz', {});
  C.unxz = function (a, i) { this.cmdLabel = 'unxz'; try { return C.xz.call(this, ['-d'].concat(a), i); } finally { this.cmdLabel = ''; } };
  C.xzcat = function (a, i) { this.cmdLabel = 'xzcat'; try { return C.xz.call(this, ['-d', '-c'].concat(a), i); } finally { this.cmdLabel = ''; } };
  C.bzip2 = squeezer('bz2', {});
  C.bunzip2 = function (a, i) { this.cmdLabel = 'bunzip2'; try { return C.bzip2.call(this, ['-d'].concat(a), i); } finally { this.cmdLabel = ''; } };
  C.bzcat = function (a, i) { this.cmdLabel = 'bzcat'; try { return C.bzip2.call(this, ['-d', '-c'].concat(a), i); } finally { this.cmdLabel = ''; } };

  C.zip = function (a) {
    const [f, rest] = opts(a);
    if (rest.length < 1) { this.out('zip error: Nothing to do! (try: zip -r archive.zip folder)\n'); return 12; }
    let out = rest.shift();
    if (!/\.\w+$/.test(baseName(out))) out += '.zip';
    if (!rest.length) { this.eout(`\nzip error: Nothing to do! (${out})\n`); return 12; }
    const fp = this.abs(out), old = this.node(fp), prev = old && this.unpack(old.data);
    const items = prev && prev.kind === 'zip' ? prev.items.slice() : [];
    let code = 0;
    this.cmdName = 'zip';
    rest.forEach(t => {
      const got = [];
      const n = this.node(this.abs(t), false);
      if (!n) { this.out(`\tzip warning: name not matched: ${t}\n`); code = 12; return; }
      if (n.type === 'd' && !f.r) got.push({ path: t.replace(/\/*$/, '/'), type: 'd', mode: n.mode, owner: n.owner, group: n.group, mtime: n.mtime });
      else this.collect(this.abs(t), t.replace(/^\/+/, ''), got, () => false);
      got.forEach(it => {
        const i = items.findIndex(x => x.path === it.path);
        const el = it.data ? this.info(it.data) : 0;
        const how = !el || el < 64 ? 'stored 0%' : `deflated ${Math.round((1 - (Math.ceil(el * 0.4) + 30) / enc(it.data)) * 100)}%`;
        if (!f.q) this.out(`  ${i >= 0 ? 'updating' : 'adding'}: ${it.path} (${how})\n`);
        it.how = how;
        if (i >= 0) items[i] = it; else items.push(it);
      });
    });
    this.cmdName = '';
    if (!items.length) { this.out(`\nzip error: Nothing to do! (${out})\n`); return 12; }
    const size = items.reduce((s, it) => s + 76 + 2 * enc(it.path) + (it.data ? (it.how.startsWith('stored') ? enc(it.data) : Math.ceil(this.info(it.data) * 0.4) + 30) : 0), 22);
    const data = this.pack({ kind: 'zip', items, size });
    if (old) { old.data = data; old.mtime = this.now(); } else {
      const parent = this.node(dirName(fp));
      if (!parent || !this.can(parent, 'w')) { this.out(`zip I/O error: Permission denied\nzip error: Could not create output file (${out})\n`); return 15; }
      this.mk(fp, 'f', 0o666 & ~this.umask, this.user, data).mtime = this.now();
    }
    return code;
  };
  C.unzip = function (a) {
    const [f, rest] = opts(a, 'd');
    const z = rest.shift();
    if (!z) { this.out('UnZip 6.00. Usage: unzip [-l] [-o] [-q] file.zip [names] [-d exdir]\n'); return 0; }
    const n = this.node(this.abs(z)) || this.node(this.abs(z + '.zip'));
    if (!n) { this.out(`unzip:  cannot find or open ${z}, ${z}.zip or ${z}.ZIP.\n`); return 9; }
    const p = this.unpack(n.data);
    if (!p || p.kind !== 'zip') { this.out(`Archive:  ${z}\n  End-of-central-directory signature not found.  Either this file is not\n  a zipfile, or it constitutes one disk of a multi-part archive.\n`); return 9; }
    const pick = p.items.filter(it => !rest.length || rest.some(g => globRe(g).test(it.path)));
    if (f.l) {
      this.out(`Archive:  ${z}\n  Length      Date    Time    Name\n---------  ---------- -----   ----\n`);
      let tot = 0;
      pick.forEach(it => { const s = it.data ? enc(it.data) : 0; tot += s; this.out(`${pad(s, 9)}  ${isoTime(it.mtime)}   ${it.path}\n`); });
      this.out(`---------                     -------\n${pad(tot, 9)}                     ${pick.length} file${pick.length === 1 ? '' : 's'}\n`);
      return 0;
    }
    const base = f.d ? this.abs(f.d) : this.cwd, show = f.d ? f.d.replace(/\/+$/, '') + '/' : '';
    if (f.d && !this.node(base)) this.mkdirs(base);
    if (!f.q) this.out(`Archive:  ${z}\n`);
    let code = 0;
    pick.forEach(it => {
      const p2 = norm(base + '/' + it.path);
      if (it.type !== 'd' && this.node(p2, false) && !f.o) {
        if (f.n) return;
        this.out(`replace ${show}${it.path}? [y]es, [n]o, [A]ll, [N]one, [r]ename: NULL\n(EOF or read failure, treating as "[N]one" ...)\n`); f.n = true; return;
      }
      const existed = it.type === 'd' && this.node(p2);
      const why = this.lay(base, it, false);
      if (existed) return;
      if (why) { this.out(`checkdir error:  cannot create ${show}${it.path}\n                 ${why.replace('Cannot open: ', '')}\n`); code = 50; return; }
      if (!f.q) this.out(it.type === 'd' ? `   creating: ${show}${it.path}\n` : `${it.how && it.how.startsWith('deflated') ? '  inflating' : ' extracting'}: ${(show + it.path).padEnd(23)} \n`);
    });
    return code;
  };

  C.xargs = function (a, input) {
    const z = a.includes('-0'); const [f, rest] = opts(a.filter(x => x !== '-0'), 'nId'); if (z) f['0'] = true;
    const cmd = rest.length ? rest : ['echo'];
    const items = f['0'] ? input.split('\u0000').filter(x => x !== '') : f.d ? input.split(unesc(f.d)).filter(x => x !== '') : input.split(/\s+/).filter(Boolean);
    if (f.r && !items.length) return 0;
    let code = 0;
    if (f.I) { items.length && lines(input).forEach(l => { code = this.call(cmd.map(x => x.split(f.I).join(l)), '') || code; }); return code; }
    const n = f.n ? +f.n : items.length || 1;
    for (let i = 0; i < Math.max(items.length, 1); i += n) code = this.call(cmd.concat(items.slice(i, i + n)), '') || code;
    return code;
  };
  C.seq = function (a) {
    const [f, rest] = opts(a.map(x => /^-\d/.test(x) ? '\u0001' + x : x), 's');
    const nums = rest.map(x => +x.replace('\u0001', ''));
    const [s, st, e] = nums.length === 1 ? [1, 1, nums[0]] : nums.length === 2 ? [nums[0], 1, nums[1]] : nums;
    const out = []; for (let x = s; st > 0 ? x <= e : x >= e; x += st) { out.push(String(x)); if (out.length > 10000) break; }
    this.out(out.length ? out.join(f.s ? unesc(f.s) : '\n') + '\n' : '');
  };
  C.basename = function (a) { let b = baseName(a[0] || ''); if (a[1] && b.endsWith(a[1])) b = b.slice(0, -a[1].length); this.out(b + '\n'); };
  C.dirname = function (a) { this.out(dirName(a[0] || '.') === '/' && !(a[0] || '').startsWith('/') ? '.\n' : (a[0].includes('/') ? dirName(a[0]) : '.') + '\n'); };
  C.export = function (a) {
    if (!a.length || a[0] === '-p') { [...this.exported].sort().forEach(k => this.out(`declare -x ${k}="${this.vars[k] ?? ''}"\n`)); return 0; }
    if (a[0] === '-n') { a.slice(1).forEach(k => this.exported.delete(k)); return 0; }
    if (a[0] === '-f') { let bad = 0; a.slice(1).forEach(k => { if (!(this.fns && this.fns[k])) { this.eout(`bash: export: ${k}: not a function\n`); bad = 1; } }); return bad; }
    let code = 0;
    a.forEach(x => { const k = x.indexOf('='); const nm = k > 0 ? x.slice(0, k) : x; if (!/^[A-Za-z_]\w*$/.test(nm)) { this.eout(`bash: export: \`${x}': not a valid identifier\n`); code = 1; return; } if (k > 0) { if (this.ro && this.ro.has(nm)) { this.eout(`bash: ${nm}: readonly variable\n`); code = 1; return; } this.vars[nm] = x.slice(k + 1); } this.exported.add(nm); });
    return code;
  };
  C.printenv = function (a) {
    if (a.length) { let code = 0; a.forEach(k => { const v = this.vars[k]; if (v === undefined || !this.exported.has(k)) code = 1; else this.out(v + '\n'); }); return code; }
    [...this.exported].sort().forEach(k => { if (this.vars[k] !== undefined) this.out(`${k}=${this.vars[k]}\n`); });
    return 0;
  };
  C.env = function (a, input) {
    let i = 0, clean = false; const unset = [], set = [];
    for (; i < a.length; i++) {
      if (a[i] === '-i' || a[i] === '-' || a[i] === '--ignore-environment') clean = true;
      else if (a[i] === '-u') unset.push(a[++i]);
      else if (/^[A-Za-z_]\w*=/.test(a[i])) set.push(a[i]);
      else break;
    }
    const keep = { vars: this.vars, ex: this.exported };
    const v = clean ? {} : this.childVars(); unset.forEach(k => delete v[k]);
    set.forEach(x => { const k = x.indexOf('='); v[x.slice(0, k)] = x.slice(k + 1); });
    this.vars = v; this.exported = new Set(Object.keys(v));
    try {
      if (i >= a.length) { Object.keys(v).sort().forEach(k => this.out(`${k}=${v[k]}\n`)); return 0; }
      if (clean && !a[i].includes('/') && !C[a[i]]) { this.eout(`env: '${a[i]}': No such file or directory\n`); return 127; }
      return this.call(a.slice(i), input);
    } finally { this.vars = keep.vars; this.exported = keep.ex; }
  };
  C.declare = C.typeset = function (a) {
    const flags = new Set(); const names = [];
    a.forEach(x => { if (/^[-+][a-zA-Z]+$/.test(x)) [...x.slice(1)].forEach(c => flags.add((x[0] === '+' ? '+' : '') + c)); else names.push(x); });
    const show = k => {
      const A = this.arrays && this.arrays[k], isA = A !== undefined && !(k in this.vars), isAs = this.assoc && this.assoc.has(k);
      const f = (isAs ? 'A' : isA ? 'a' : '') + (this.exported.has(k) ? 'x' : '') + (this.ro && this.ro.has(k) ? 'r' : '');
      if (isA) { const body = this.arrKeys(k).map(key => `[${key}]="${this.arrGet(k, isAs ? key : String(key), true)}"`).join(' '); this.out(`declare -${f} ${k}=(${body}${isAs && body ? ' ' : ''})\n`); return; }
      this.out(`declare -${f || '-'} ${k}="${this.vars[k] ?? ''}"\n`);
    };
    if (!names.length) {
      const keys = [...new Set(Object.keys(this.vars).concat(Object.keys(this.arrays || {}).filter(k => k !== 'PIPESTATUS')))].sort();
      if (flags.has('x')) keys.filter(k => this.exported.has(k)).forEach(show);
      else if (flags.has('r')) keys.filter(k => this.ro && this.ro.has(k)).forEach(show);
      else if (flags.has('f') || flags.has('F')) Object.keys(this.fns || {}).sort().forEach(k => this.out(`declare -f ${k}\n`));
      else keys.forEach(k => this.out(`${k}=${this.vars[k]}\n`));
      return 0;
    }
    let code = 0;
    names.forEach(x => {
      const k = x.includes('=') ? x.slice(0, x.indexOf('=')) : x;
      if (flags.has('p')) { if (k in this.vars || (this.arrays && this.arrays[k] !== undefined)) show(k); else { this.eout(`bash: declare: ${k}: not found\n`); code = 1; } return; }
      if (this.ro && this.ro.has(k) && x.includes('=')) { this.eout(`bash: ${k}: readonly variable\n`); code = 1; return; }
      if (flags.has('A')) { this.assoc = this.assoc || new Set(); this.assoc.add(k); this.arrays = this.arrays || {}; if (!this.arrays[k] || Array.isArray(this.arrays[k])) this.arrays[k] = {}; delete this.vars[k]; }
      if (flags.has('a') && !(this.arrays && this.arrays[k])) { (this.arrays = this.arrays || {})[k] = []; delete this.vars[k]; }
      if (x.includes('=') && /^[\w]+(\+?)=\(/.test(x) && x.endsWith(')')) { const app = x[k.length] === '+'; this.setArr({ name: k, list: this.arrayItems(x.slice(x.indexOf('(') + 1, -1), k), app }); if (flags.has('x')) this.exported.add(k); if (flags.has('r')) { this.ro = this.ro || new Set(); this.ro.add(k); } return; }
      if (x.includes('=')) { let val = x.slice(k.length + 1); if (flags.has('i')) { try { val = String(this.arith(val)); } catch (e) { val = '0'; } } if (flags.has('u')) val = val.toUpperCase(); if (flags.has('l')) val = val.toLowerCase(); this.vars[k] = val; }
      else if (!(k in this.vars)) this.vars[k] = '';
      if (flags.has('x')) this.exported.add(k); if (flags.has('+x')) this.exported.delete(k);
      if (flags.has('r')) { this.ro = this.ro || new Set(); this.ro.add(k); }
    });
    return code;
  };
  C.readonly = function (a) {
    if (!a.length || a[0] === '-p') { [...(this.ro || [])].sort().forEach(k => this.out(`declare -r ${k}="${this.vars[k] ?? ''}"\n`)); return 0; }
    return C.declare.call(this, ['-r'].concat(a));
  };
  C.set = function (a) {
    if (!a.length) { Object.keys(this.vars).sort().forEach(k => this.out(`${k}=${this.vars[k]}\n`)); return 0; }
    this.opts = this.opts || {};
    const long = { e: 'errexit', u: 'nounset', x: 'xtrace', C: 'noclobber' };
    for (let i = 0; i < a.length; i++) {
      const x = a[i];
      if (x === '-o' || x === '+o') {
        const name = a[++i];
        if (!name) { ['errexit', 'noclobber', 'nounset', 'pipefail', 'xtrace'].forEach(k => this.out(`${k.padEnd(15)}\t${this.opts[k] ? 'on' : 'off'}\n`)); continue; }
        if (!['errexit', 'noclobber', 'nounset', 'pipefail', 'xtrace'].includes(name)) { this.eout(`bash: set: ${name}: invalid option name\n`); return 2; }
        this.opts[name] = x === '-o'; continue;
      }
      if (/^[-+][euxCo]+$/.test(x)) { for (const ch of x.slice(1)) { if (ch === 'o') { const name = a[++i]; if (!['errexit', 'noclobber', 'nounset', 'pipefail', 'xtrace'].includes(name)) { this.eout(`bash: set: ${name}: invalid option name\n`); return 2; } this.opts[name] = x[0] === '-'; } else this.opts[long[ch]] = x[0] === '-'; } continue; }
      if (x === '--') { this.args = a.slice(i + 1); break; }
      this.eout(`bash: set: ${x}: invalid option\n`); return 2;
    }
    return 0;
  };
  C.unset = function (a) {
    let code = 0;
    a.filter(k => k !== '-v' && k !== '-f').forEach(k => {
      const m = /^(\w+)\[(.+)\]$/.exec(k);
      if (m) { const A = this.arrays && this.arrays[m[1]]; if (!A) return; if (Array.isArray(A)) { const ix = this.arith(m[2]); delete A[ix < 0 ? A.length + ix : ix]; } else delete A[this.expandStr(m[2])]; return; }
      if (this.ro && this.ro.has(k)) { this.eout(`bash: unset: ${k}: cannot unset: readonly variable\n`); code = 1; return; }
      delete this.vars[k]; this.exported.delete(k); if (this.arrays) delete this.arrays[k]; if (this.assoc) this.assoc.delete(k);
      if (a[0] === '-f' && this.fns) delete this.fns[k];
    });
    return code;
  };
  C.alias = function (a) {
    if (!a.length) { Object.keys(this.aliases).sort().forEach(k => this.out(`alias ${k}='${this.aliases[k]}'\n`)); return 0; }
    let code = 0;
    a.forEach(x => { const k = x.indexOf('='); if (k > 0) this.aliases[x.slice(0, k)] = x.slice(k + 1); else if (this.aliases[x]) this.out(`alias ${x}='${this.aliases[x]}'\n`); else { this.eout(`bash: alias: ${x}: not found\n`); code = 1; } });
    return code;
  };
  C.unalias = function (a) { a.forEach(k => delete this.aliases[k]); };
  /* ---------- processes, jobs and signals ----------
     Every process is {pid, ppid, user, cmd, stat, ni, start}. A job is a background command typed in this shell:
     {id, pid, cmd, state: Running | Stopped | Done | Terminated | Killed | Interrupt | Hangup, end, told}.
     The practice shell has a pretend clock: sleep N moves it forward, and a background sleep ends when the
     clock passes its end time. Other background commands run straight away and are reported Done. */
  const SIGS = ['', 'HUP', 'INT', 'QUIT', 'ILL', 'TRAP', 'ABRT', 'BUS', 'FPE', 'KILL', 'USR1', 'SEGV', 'USR2', 'PIPE', 'ALRM', 'TERM', 'STKFLT', 'CHLD', 'CONT', 'STOP', 'TSTP', 'TTIN', 'TTOU', 'URG', 'XCPU', 'XFSZ', 'VTALRM', 'PROF', 'WINCH', 'IO', 'PWR', 'SYS'];
  const sigName = n => n <= 31 ? SIGS[n] : n === 34 ? 'RTMIN' : n === 64 ? 'RTMAX' : n < 50 ? 'RTMIN+' + (n - 34) : 'RTMAX-' + (64 - n);
  const sigNum = s => { s = String(s).toUpperCase().replace(/^SIG/, ''); if (/^\d+$/.test(s)) return +s <= 64 ? +s : -1; const i = SIGS.indexOf(s); return i > 0 ? i : -1; };
  const DEATH = { 1: 'Hangup', 2: 'Interrupt', 3: 'Quit', 9: 'Killed', 15: 'Terminated' };
  const srcWord = w => w.parts.map(p => p.q === 1 ? `'${p.t}'` : p.q === 2 ? `"${p.t}"` : p.t).join('');
  World.prototype.srcOf = function (n) {
    if (!n) return '';
    if (n.t === 'cmd') return n.words.map(srcWord).concat((n.redir || []).map(r => r.op + (r.w ? ' ' + srcWord(r.w) : ''))).join(' ');
    if (n.t === 'pipe') return n.cmds.map(c => this.srcOf(c)).join(' | ');
    if (n.t === 'and' || n.t === 'or') return this.srcOf(n.a) + (n.t === 'and' ? ' && ' : ' || ') + this.srcOf(n.b);
    return '...';
  };
  const comm = p => p.comm || baseName(p.cmd.split(' ')[0]);
  World.prototype.proc = function (pid) { return this.procs.find(p => p.pid === pid); };
  /* bash makes the most recently stopped job the current one (+), otherwise the newest job. - is the one before */
  World.prototype.order = function () {
    const js = this.jobs.filter(j => !j.gone), live = j => j && !j.gone;
    const cur = live(this.curJob) ? this.curJob : js[js.length - 1];
    const rest = js.filter(j => j !== cur);
    const prev = live(this.prevJob) && this.prevJob !== cur ? this.prevJob : rest[rest.length - 1];
    return { cur, prev };
  };
  World.prototype.makeCur = function (j) { if (this.curJob !== j) { this.prevJob = this.curJob; this.curJob = j; } };
  World.prototype.mark = function (j) { const o = this.order(); return j === o.cur ? '+' : j === o.prev ? '-' : ' '; };
  World.prototype.jobOf = function (spec) {
    const js = this.jobs.filter(j => !j.gone);
    if (spec === undefined || spec === '%' || spec === '%%' || spec === '%+') return this.order().cur;
    if (spec === '%-') return this.order().prev;
    const m = /^%(\d+)$/.exec(spec); if (m) return js.find(j => j.id === +m[1]);
    const n = /^%(.+)$/.exec(spec); if (n) return js.find(j => j.cmd.startsWith(n[1]));
    return null;
  };
  /* start a background job for one list item */
  World.prototype.background = function (node, input) {
    const js = this.jobs.filter(j => !j.gone);
    const id = js.length ? js[js.length - 1].id + 1 : 1, pid = this.nextPid++, cmd = this.srcOf(node);
    this.out(`[${id}] ${pid}\n`);
    this.lastBg = pid;
    const job = { id, pid, cmd, state: 'Running', told: false };
    this.jobs.push(job); this.makeCur(job);
    const first = node.t === 'pipe' && node.cmds.length === 1 ? node.cmds[0] : node;
    const words = first.t === 'cmd' ? first.words.map(w => this.wordText(w)) : [];
    let lead = words[0] === 'nohup' || words[0] === 'nice' ? words.slice(words[0] === 'nice' && words[1] === '-n' ? 3 : 1) : words;
    if (lead[0] === 'sleep' && parseFloat(lead[1]) > 0 || lead[0] === 'yes' && /\/dev\/null/.test(cmd)) {
      job.end = lead[0] === 'yes' ? Infinity : this.clock + parseFloat(lead[1]) * 1000;
      this.procs.push({ pid, ppid: 2001, user: this.user, cmd: lead.join(' '), stat: 'S', ni: words[0] === 'nice' ? (words[1] === '-n' ? +words[2] : 10) : 0, start: this.clock, cpu: lead[0] === 'yes' ? 99.7 : 0 });
      if (words[0] === 'nohup') { this.eout("nohup: ignoring input and appending output to 'nohup.out'\n"); const f = this.abs('nohup.out'); if (!this.node(f)) this.mk(f, 'f', 0o600, this.user, ''); }
      return 0;
    }
    const code = this.exec(node, input);
    job.state = code ? `Exit ${code}` : 'Done'; job.fresh = true;
    return 0;
  };
  /* move the clock on and report jobs that changed, the way bash does just before it prints the next prompt */
  World.prototype.reap = function () {
    this.jobs.forEach(j => {
      if (j.state === 'Running' && j.end !== undefined && this.clock >= j.end) { j.state = 'Done'; this.procs = this.procs.filter(p => p.pid !== j.pid); }
    });
    const live = this.jobs.filter(j => !j.gone);
    live.forEach((j, k) => {
      if (j.fresh) { j.fresh = false; return; }
      if (j.state !== 'Running' && j.state !== 'Stopped' && !j.told) {
        this.out(`[${j.id}]${this.mark(j)}  ${pad(j.state, 24, true)}${j.cmd}\n`);
        j.told = true; j.gone = true;
      }
    });
    if (this.jobs.every(j => j.gone)) this.jobs = [];
  };
  World.prototype.signal = function (pid, sig, who) {
    if (pid === 2001) {
      const name = sigName(sig);
      if (this.traps && this.traps[name] !== undefined) { if (this.traps[name] !== '') this.runTrap(name); return 0; }
      if (sig === 0 || sig === 17 || sig === 18 || sig === 28 || sig === 23) return 0;
      if (this.script) throw { exit: 128 + sig, sig };
      if (sig === 2 || sig === 15 || sig === 3) return 0;   /* an interactive shell ignores INT, TERM and QUIT */
    }
    const p = this.proc(pid);
    if (!p) { this.eout(`${who}: (${pid}) - No such process\n`); return 1; }
    if (p.user !== this.user && this.user !== 'root') { this.eout(`${who}: (${pid}) - Operation not permitted\n`); return 1; }
    if (pid === 1 && sig !== 0) return 0;   /* init ignores signals it has no handler for */
    const job = this.jobs.find(j => j.pid === pid && !j.gone);
    if (sig === 0) return 0;
    if (sig === 19 || sig === 20) { p.stat = 'T'; if (job) { job.state = 'Stopped'; this.makeCur(job); this.out(`\n[${job.id}]+  ${pad('Stopped', 24, true)}${job.cmd}\n`); } return 0; }
    if (sig === 18) { p.stat = 'S'; if (job) job.state = 'Running'; return 0; }
    if (sig === 28 || sig === 17 || sig === 23) return 0;   /* WINCH, CHLD and URG are ignored by default */
    if (p.stat === 'T' && sig !== 9) { p.pending = sig; return 0; }   /* a stopped process sees the signal when it continues */
    this.procs = this.procs.filter(x => x.pid !== pid && x.ppid !== pid);
    if (job) job.state = DEATH[sig] || `Killed by signal ${sig}`;
    return 0;
  };
  C.kill = function (a) {
    let sig = 15; const targets = [];
    for (let i = 0; i < a.length; i++) {
      const x = a[i];
      if (x === '-l' || x === '-L') {
        const rest = a.slice(i + 1);
        if (rest.length) { rest.forEach(r => { const n = /^\d+$/.test(r) ? (+r > 128 ? +r - 128 : +r) : sigNum(r); this.out((/^\d+$/.test(r) ? sigName(n) : n) + '\n'); }); return 0; }
        const all = []; for (let n = 1; n <= 64; n++) if (n !== 32 && n !== 33) all.push(`${pad(n, 2)}) SIG${sigName(n)}`);
        let s = ''; all.forEach((e, k) => { s += e + ((k + 1) % 5 === 0 || k === all.length - 1 ? '\n' : '\t'); }); this.out(s); return 0;
      }
      if (x === '-s' || x === '-n') { sig = sigNum(a[++i]); if (sig < 0) { this.eout(`bash: kill: ${a[i]}: invalid signal specification\n`); return 1; } continue; }
      if (/^-[A-Za-z0-9+]+$/.test(x) && !targets.length) { sig = sigNum(x.slice(1)); if (sig < 0) { this.eout(`bash: kill: ${x.slice(1)}: invalid signal specification\n`); return 1; } continue; }
      targets.push(x);
    }
    if (!targets.length) { this.eout('kill: usage: kill [-s sigspec | -n signum | -sigspec] pid | jobspec ... or kill -l [sigspec]\n'); return 2; }
    let code = 0;
    targets.forEach(t => {
      if (t.startsWith('%')) { const j = this.jobOf(t); if (!j) { this.eout(`bash: kill: ${t}: no such job\n`); code = 1; return; } if (j.state !== 'Running' && j.state !== 'Stopped') { this.eout(`bash: kill: ${t}: no such job\n`); code = 1; return; } code = this.signal(j.pid, sig, 'bash: kill') || code; return; }
      if (!/^-?\d+$/.test(t)) { this.eout(`bash: kill: ${t}: arguments must be process or job IDs\n`); code = 1; return; }
      code = this.signal(+t, sig, 'bash: kill') || code;
    });
    return code;
  };
  C.jobs = function (a) {
    const [f] = opts(a); const live = this.jobs.filter(j => !j.gone);
    live.forEach((j, k) => {
      if (f.p) { this.out(j.pid + '\n'); return; }
      if (f.r && j.state !== 'Running' || f.s && j.state !== 'Stopped') return;
      const mark = this.mark(j);
      this.out(`[${j.id}]${mark}${f.l ? ' ' + j.pid + ' ' : '  '}${pad(j.state, 24, true)}${j.cmd}${j.state === 'Running' ? ' &' : ''}\n`);
      if (j.state !== 'Running' && j.state !== 'Stopped') { j.told = true; j.gone = true; }
    });
    return 0;
  };
  C.fg = function (a) {
    const j = this.jobOf(a[0]);
    if (!j || j.gone) { this.eout(`bash: fg: ${a[0] || 'current'}: no such job\n`); return 1; }
    this.out(j.cmd + '\n');
    const p = this.proc(j.pid);
    if (p) { p.stat = 'S'; if (p.pending) { const s = p.pending; p.pending = 0; this.signal(j.pid, s, 'fg'); j.told = true; j.gone = true; return 128 + s; } }
    if (j.end === Infinity) { this.out('^C\n'); this.procs = this.procs.filter(x => x.pid !== j.pid); j.gone = true; return 130; }
    if (j.end !== undefined && this.clock < j.end) this.clock = j.end;
    this.procs = this.procs.filter(x => x.pid !== j.pid);
    j.gone = true; j.told = true;
    return 0;
  };
  C.bg = function (a) {
    const j = this.jobOf(a[0]);
    if (!j || j.gone) { this.eout(`bash: bg: ${a[0] || 'current'}: no such job\n`); return 1; }
    if (j.state === 'Running') { this.eout(`bash: bg: job ${j.id} already in background\n`); return 0; }
    j.state = 'Running'; this.makeCur(j); const p = this.proc(j.pid); if (p) p.stat = 'S';
    this.out(`[${j.id}]${this.mark(j)} ${j.cmd} &\n`);
    return 0;
  };
  C.wait = function (a) {
    const pick = a.length ? a.map(t => t.startsWith('%') ? this.jobOf(t) : this.jobs.find(j => j.pid === +t)).filter(Boolean) : this.jobs.filter(j => j.state === 'Running');
    let code = 0;
    pick.forEach(j => {
      if (j.state === 'Running' && j.end !== undefined && j.end !== Infinity) { this.clock = Math.max(this.clock, j.end); j.state = 'Done'; this.procs = this.procs.filter(p => p.pid !== j.pid); }
      const sig = Object.keys(DEATH).find(k => DEATH[k] === j.state);
      code = j.state === 'Done' ? 0 : sig ? 128 + +sig : /^Exit (\d+)/.test(j.state) ? +RegExp.$1 : 0;
      j.told = true; j.gone = true;
    });
    return code;
  };
  C.disown = function (a) { const j = this.jobOf(a[0]); if (!j) { this.eout(`bash: disown: ${a[0] || 'current'}: no such job\n`); return 1; } j.gone = true; j.told = true; const p = this.proc(j.pid); if (p) p.ppid = 1; return 0; };
  C.sleep = function (a) {
    const n = parseFloat(a[0]);
    if (isNaN(n)) { this.eout(a[0] ? `sleep: invalid time interval '${a[0]}'\n` : "sleep: missing operand\nTry 'sleep --help' for more information.\n"); return 1; }
    this.clock += n * (/m$/.test(a[0]) ? 60000 : /h$/.test(a[0]) ? 3600000 : 1000);
    return 0;
  };
  World.prototype.allProcs = function () { return this.procs.concat([{ pid: this.nextPid, ppid: 2001, user: this.user, cmd: 'ps', stat: 'R', ni: 0, start: this.clock, me: true }]); };
  C.ps = function (a) {
    const flat = a.join(' ');
    const all = /(^|\s)(-e|-A|aux|ax|-ef|-aux|-eo)\b/.test(flat) || /^a?u?x$/.test(flat);
    let rows = all ? this.allProcs() : this.allProcs().filter(p => p.user === this.user);
    const pi = a.indexOf('-p'), ui = a.indexOf('-u'), ci = a.indexOf('-C');
    if (pi >= 0) rows = this.allProcs().filter(p => a[pi + 1].split(',').map(Number).includes(p.pid));
    if (ui >= 0) rows = this.allProcs().filter(p => a[ui + 1].split(',').includes(p.user));
    if (ci >= 0) rows = this.allProcs().filter(p => comm(p) === a[ci + 1]);
    const tty = p => p.ppid === 2001 || p.pid === 2001 ? 'pts/0' : '?';
    const t0 = p => when(p.start || T0 - 3 * 86400000).slice(7);
    const oi = a.findIndex(x => x === '-o' || x === '-eo' || x === 'o');
    if (oi >= 0) {
      const cols = a[oi + 1].split(',');
      const H = { pid: ['PID', 7], ppid: ['PPID', 7], user: ['USER', -8], stat: ['STAT', -4], ni: ['NI', 3], comm: ['COMMAND', -15], cmd: ['CMD', 0], args: ['COMMAND', 0], '%cpu': ['%CPU', 4], '%mem': ['%MEM', 4], tty: ['TT', -8], etime: ['ELAPSED', 11] };
      const val = (p, c) => ({ pid: p.pid, ppid: p.ppid, user: p.user, stat: p.stat + (p.pid === 2001 ? 's' : ''), ni: p.ni || 0, comm: comm(p), cmd: p.cmd, args: p.cmd, '%cpu': (p.cpu || 0).toFixed(1), '%mem': '0.1', tty: tty(p), etime: '00:' + pad(Math.max(0, Math.round((this.clock - (p.start || T0)) / 1000)) % 60, 2).replace(' ', '0') })[c];
      const line = f => cols.map((c, k) => { const [, w] = H[c] || [c.toUpperCase(), 8]; const s = String(f(c)); return k === cols.length - 1 && w <= 0 ? s : w < 0 ? pad(s, -w, true) : pad(s, w); }).join(' ');
      this.out(line(c => (H[c] || [c.toUpperCase()])[0]).replace(/\s+$/, '') + '\n' + rows.map(p => line(c => val(p, c))).join('\n') + '\n');
      return 0;
    }
    if (/u/.test(flat) && !/-u/.test(flat)) { this.out('USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n' + rows.map(p => `${pad(p.user, 8, true)} ${pad(p.pid, 7)} ${pad((p.cpu || 0).toFixed(1), 4)}  0.1  ${pad(p.pid === 1 ? 167700 : 8000 + p.pid % 900 * 7, 6)} ${pad(p.pid === 1 ? 13020 : 3000 + p.pid % 700 * 3, 5)} ${pad(tty(p), 8, true)} ${pad(p.stat + (p.pid === 2001 || p.pid === 1 ? 's' : ''), 4, true)} ${pad(t0(p), 5)}   0:00 ${p.cmd}`).join('\n') + '\n'); return 0; }
    if (/-ef|-f/.test(flat)) { this.out('UID          PID    PPID  C STIME TTY          TIME CMD\n' + rows.map(p => `${pad(p.user, 8, true)} ${pad(p.pid, 7)} ${pad(p.ppid, 7)}  0 ${t0(p)} ${pad(tty(p), 8, true)} 00:00:00 ${p.cmd}`).join('\n') + '\n'); return 0; }
    this.out('    PID TTY          TIME CMD\n' + rows.map(p => `${pad(p.pid, 7)} ${pad(tty(p), 8, true)} 00:00:00 ${comm(p)}`).join('\n') + '\n');
    return 0;
  };
  C.pgrep = function (a) {
    const [f, rest] = opts(a, 'u');
    const re = new RegExp(rest[0] || '^$');
    const hits = this.procs.filter(p => (f.f ? re.test(p.cmd) : re.test(comm(p))) && (!f.u || p.user === f.u));
    hits.forEach(p => this.out(f.l || f.a ? `${p.pid} ${f.a ? p.cmd : comm(p)}\n` : p.pid + '\n'));
    return hits.length ? 0 : 1;
  };
  C.pkill = function (a) {
    let sig = 15; const b = a.filter(x => { if (/^-[A-Z]+$|^-\d+$/.test(x)) { sig = sigNum(x.slice(1)); return false; } return true; });
    const [f, rest] = opts(b, 'u'); const re = new RegExp(rest[0] || '^$');
    const hits = this.procs.filter(p => (f.f ? re.test(p.cmd) : re.test(comm(p))) && (!f.u || p.user === f.u));
    let denied = false;
    hits.forEach(p => { if (!this.proc(p.pid)) return; if (p.user !== this.user && this.user !== 'root') { this.eout(`pkill: killing pid ${p.pid} failed: Operation not permitted\n`); denied = true; } else this.signal(p.pid, sig, 'pkill'); });
    return hits.length && !denied ? 0 : hits.length ? 1 : 1;
  };
  C.killall = function (a) {
    let sig = 15; const names = a.filter(x => { if (/^-[A-Z]+$|^-\d+$/.test(x)) { sig = sigNum(x.slice(1)); return false; } return !x.startsWith('-'); });
    let code = 0;
    names.forEach(nm => {
      const hits = this.procs.filter(p => comm(p) === nm);
      if (!hits.length) { this.eout(`${nm}: no process found\n`); code = 1; return; }
      hits.forEach(p => { if (!this.proc(p.pid)) return; if (p.user !== this.user && this.user !== 'root') { this.eout(`${nm}(${p.pid}): Operation not permitted\n`); code = 1; } else this.signal(p.pid, sig, 'killall'); });
    });
    return code;
  };
  C.nohup = function (a, input) {
    if (!a.length) { this.eout("nohup: missing operand\nTry 'nohup --help' for more information.\n"); return 125; }
    if (this.notty) return this.call(a, input);
    this.eout("nohup: ignoring input and appending output to 'nohup.out'\n");
    const f = this.abs('nohup.out'), n = this.node(f) || this.mk(f, 'f', 0o600, this.user, '');
    let buf = ''; const save = this.outHook; this.outHook = s => { buf += s; };
    let code; try { code = this.call(a, input); } finally { this.outHook = save; }
    n.data += buf; n.mtime = this.now();
    return code;
  };
  C.nice = function (a, input) {
    if (!a.length) { this.out('0\n'); return 0; }
    let k = 0, n = 10;
    if (a[0] === '-n') { n = +a[1]; k = 2; } else if (/^-\d+$/.test(a[0])) { n = +a[0].slice(1); k = 1; }
    if (n < 0 && this.user !== 'root') this.eout('nice: cannot set niceness: Permission denied\n');
    return this.call(a.slice(k), input);
  };
  C.renice = function (a) {
    let n = 0, i = 0;
    if (a[0] === '-n') { n = +a[1]; i = 2; } else { n = +a[0]; i = 1; }
    if (a[i] === '-p') i++;
    let code = 0;
    a.slice(i).forEach(t => {
      const p = this.proc(+t);
      if (!p) { this.eout(`renice: failed to get priority for ${t} (process ID): No such process\n`); code = 1; return; }
      if (p.user !== this.user && this.user !== 'root' || n < (p.ni || 0) && this.user !== 'root') { this.eout(`renice: failed to set priority for ${t} (process ID): Permission denied\n`); code = 1; return; }
      this.out(`${t} (process ID) old priority ${p.ni || 0}, new priority ${n}\n`); p.ni = n;
    });
    return code;
  };
  C.top = function () {
    const rows = this.allProcs().filter(p => !p.me).sort((x, y) => (y.cpu || 0) - (x.cpu || 0) || x.pid - y.pid);
    const busy = rows.reduce((s, p) => s + (p.cpu || 0), 0) / 2;
    this.out(`(the practice shell prints one screen, like top -b -n 1. A real top redraws every 3 seconds: q quits, k kills, M sorts by memory, P by CPU)\ntop - ${when(this.clock).slice(7)}:00 up 3 days,  2:41,  1 user,  load average: ${(0.3 + busy / 50).toFixed(2)}, 0.35, 0.30\nTasks: ${pad(rows.length, 3)} total,   ${rows.filter(p => p.cpu).length} running, ${pad(rows.filter(p => !p.cpu && p.stat !== 'T').length, 3)} sleeping,   ${rows.filter(p => p.stat === 'T').length} stopped,   0 zombie\n%Cpu(s): ${pad(busy.toFixed(1), 4)} us,  0.3 sy,  0.0 ni, ${pad((99.7 - busy).toFixed(1), 4)} id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st\nMiB Mem :   7859.4 total,   5120.6 free,   1210.3 used,   1528.5 buff/cache\nMiB Swap:   2048.0 total,   2048.0 free,      0.0 used.   6420.1 avail Mem\n\n    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n` +
      rows.map(p => `${pad(p.pid, 7)} ${pad(p.user, 9, true)} ${pad(20 + (p.ni || 0), 3)} ${pad(p.ni || 0, 3)} ${pad(p.pid === 1 ? 167700 : 8000 + p.pid % 900 * 7, 7)} ${pad(3000 + p.pid % 700 * 3, 6)} ${pad(2200, 6)} ${p.cpu ? 'R' : p.stat === 'T' ? 'T' : 'S'} ${pad((p.cpu || 0).toFixed(1), 5)}   0.1   0:00.${pad(p.pid % 100, 2).replace(' ', '0')} ${comm(p)}`).join('\n') + '\n');
    return 0;
  };
  C.time = function (a, input) {
    const t0 = this.clock, code = this.call(a, input), secs = Math.max(0, (this.clock - t0) / 1000);
    this.eout(`\nreal\t${Math.floor(secs / 60)}m${(secs % 60 + 0.002).toFixed(3)}s\nuser\t0m0.001s\nsys\t0m0.001s\n`);
    return code;
  };
  C.yes = function (a) { const w = (a.length ? a.join(' ') : 'y') + '\n'; if (this.notty) { this.out(w.repeat(2000)); return 0; } this.out(w.repeat(12) + '^C\n(yes never stops on its own. In a real terminal press Ctrl+C. Here it was stopped after 12 lines)\n'); return 130; };
  C.true = function () { return 0; };
  C.false = function () { return 1; };
  C.exit = function (a) { throw { exit: a[0] === undefined ? this.last : +a[0] }; };
  C.logout = C.exit;
  C.return = function (a) { throw { ret: a[0] === undefined ? this.last : +a[0] }; };
  C.break = function (a) { throw { brk: Math.max(1, +a[0] || 1) }; };
  C.continue = function (a) { throw { cont: Math.max(1, +a[0] || 1) }; };
  C.read = function (a, input) {
    const [f, rest] = opts(a, 'pad');
    let line;
    const dl = f.d === undefined ? '\n' : f.d === '' ? '\u0000' : f.d[0];
    if (this.cur && input === this.cur.s) {
      if (this.cur.pos >= this.cur.s.length) return 1;
      const k = this.cur.s.indexOf(dl, this.cur.pos);
      line = k < 0 ? this.cur.s.slice(this.cur.pos) : this.cur.s.slice(this.cur.pos, k);
      const full = k >= 0; this.cur.pos = k < 0 ? this.cur.s.length : k + 1;
      if (!full && line === '') return 1;
      input = full ? input : '';
    } else {
      if (f.p && !input) this.eout(f.p);
      if (!input) return 1;
      line = input.split(dl)[0];
    }
    if (!f.r) line = line.replace(/\\(.)/g, '$1');
    const ifs = this.vars.IFS ?? ' \t\n', white = /^[ \t\n]*$/.test(ifs);
    const split = (str, max) => {
      if (white) { const t = str.replace(/^[ \t\n]+|[ \t\n]+$/g, ''); if (!t) return []; if (max <= 1) return [t]; const out = []; let r = t; while (out.length < max - 1) { const m = /[ \t\n]+/.exec(r); if (!m) break; out.push(r.slice(0, m.index)); r = r.slice(m.index + m[0].length); } out.push(r); return out; }
      const out = []; let r = str; while (out.length < max - 1) { let k = -1; for (let q = 0; q < r.length; q++) if (ifs.includes(r[q])) { k = q; break; } if (k < 0) break; out.push(r.slice(0, k)); r = r.slice(k + 1); } out.push(r); return out;
    };
    if (f.a) { (this.arrays = this.arrays || {})[f.a] = split(line, Infinity); if (this.assoc) this.assoc.delete(f.a); return 0; }
    const names = rest.length ? rest : ['REPLY'];
    const parts = names.length === 1 && names[0] === 'REPLY' && !rest.length ? [line] : split(line, names.length);
    names.forEach((n, k) => { this.vars[n] = parts[k] ?? ''; });
    return 0;
  };
  /* the unary file tests of test(1) and [[ ]]. undefined means the operator is not a file test */
  World.prototype.fileTest = function (op, x) {
    const n = this.node(this.abs(x)), ln = this.node(this.abs(x), false);
    switch (op) {
      case '-e': case '-a': return !!n; case '-f': return !!n && n.type === 'f'; case '-d': return !!n && n.type === 'd'; case '-s': return !!n && this.size(n) > 0;
      case '-r': return !!n && this.can(n, 'r'); case '-w': return !!n && this.can(n, 'w'); case '-x': return !!n && this.can(n, 'x');
      case '-L': case '-h': return !!ln && ln.type === 'l'; case '-c': return !!n && n.type === 'c'; case '-b': case '-p': case '-S': return false;
      case '-O': return !!n && n.owner === this.user; case '-G': return !!n && n.group === this.user;
      case '-u': return !!n && (n.mode & 0o4000) !== 0; case '-g': return !!n && (n.mode & 0o2000) !== 0; case '-k': return !!n && (n.mode & 0o1000) !== 0;
      case '-z': return x === ''; case '-n': return x !== '';
    }
  };
  World.prototype.fileCmp = function (op, l, r) {
    const a = this.node(this.abs(l)), b = this.node(this.abs(r));
    if (op === '-ef') return !!a && a === b;
    if (!a || !b) return op === '-nt' ? !!a && !b : !a && !!b;
    return op === '-nt' ? a.mtime > b.mtime : a.mtime < b.mtime;
  };
  C.test = C['['] = function (a, _, nm) {
    if (nm === '[') { if (a[a.length - 1] !== ']') { this.eout("[: missing `]'\n"); return 2; } a = a.slice(0, -1); }
    const one = x => {
      if (x.length === 0) return false;
      if (x[0] === '!') return !one(x.slice(1));
      const ai = x.indexOf('-a'), oi = x.indexOf('-o');
      if (oi > 0) return one(x.slice(0, oi)) || one(x.slice(oi + 1));
      if (ai > 0) return one(x.slice(0, ai)) && one(x.slice(ai + 1));
      if (x.length === 1) return x[0] !== '';
      if (x.length === 2) {
        const v = this.fileTest(x[0], x[1]);
        if (v !== undefined) return v;
        throw new Error(`${x[0]}: unary operator expected`);
      }
      if (x.length > 3) throw new Error('too many arguments');
      const [l, op, r] = x;
      const N = v => { if (!/^-?\d+$/.test(v.trim())) throw new Error(`${v}: integer expression expected`); return +v; };
      switch (op) {
        case '=': case '==': return l === r; case '!=': return l !== r;
        case '-eq': return N(l) === N(r); case '-ne': return N(l) !== N(r); case '-lt': return N(l) < N(r);
        case '-le': return N(l) <= N(r); case '-gt': return N(l) > N(r); case '-ge': return N(l) >= N(r);
        case '<': return l < r; case '>': return l > r;
        case '-nt': case '-ot': case '-ef': return this.fileCmp(op, l, r);
      }
      throw new Error(`${op}: binary operator expected`);
    };
    try { return one(a) ? 0 : 1; } catch (e) { this.eout(`bash: ${nm}: ${e.message}\n`); return 2; }
  };
  C.expr = function (a) {
    let v;
    if (a.length === 3) { const [l, op, r] = a; v = { '+': +l + +r, '-': l - r, '*': l * r, '/': Math.trunc(l / r), '%': l % r, '=': +(l === r), '>': +(+l > +r), '<': +(+l < +r) }[op]; }
    else if (a[0] === 'length') v = (a[1] || '').length;
    else v = a.join(' ');
    this.out(v + '\n');
    return v === 0 || v === '' ? 1 : 0;
  };
  C.umask = function (a) {
    if (!a.length) { this.out(this.umask.toString(8).padStart(4, '0') + '\n'); return 0; }
    if (a[0] === '-S') { const m = ~this.umask & 0o777, s = sh => ['r', 'w', 'x'].filter((_, i) => m >> (sh + 2 - i) & 1).join(''); this.out(`u=${s(6)},g=${s(3)},o=${s(0)}\n`); return 0; }
    this.umask = parseInt(a[0], 8) & 0o777;
  };
  C.tree = function (a) {
    const [f, rest] = opts(a, 'L');
    const t = rest[0] || '.', root = this.node(this.abs(t));
    if (!root) { this.out(`${t}  [error opening dir]\n`); return 2; }
    let nd = 0, nf = 0; const out = [t];
    const walk = (n, pre, depth) => {
      const ks = Object.keys(n.kids).filter(k => f.a || !k.startsWith('.')).sort();
      ks.forEach((k, i) => {
        const c = n.kids[k], lastOne = i === ks.length - 1;
        out.push(pre + (lastOne ? '└── ' : '├── ') + k + (c.type === 'l' ? ' -> ' + c.target : ''));
        if (c.type === 'd') { nd++; if (!f.L || depth < +f.L) walk(c, pre + (lastOne ? '    ' : '│   '), depth + 1); } else nf++;
      });
    };
    walk(root, '', 1);
    this.out(out.join('\n') + `\n\n${nd} director${nd === 1 ? 'y' : 'ies'}, ${nf} file${nf === 1 ? '' : 's'}\n`);
  };
  C.diff = function (a) {
    const [, rest] = opts(a);
    const xs = this.inputs(rest.slice(0, 2), '', 'diff');
    if (xs.length < 2) return 2;
    const A = lines(xs[0].data), B = lines(xs[1].data);
    const m = A.length, n = B.length, L = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
    for (let i = m - 1; i >= 0; i--) for (let j = n - 1; j >= 0; j--) L[i][j] = A[i] === B[j] ? L[i + 1][j + 1] + 1 : Math.max(L[i + 1][j], L[i][j + 1]);
    let i = 0, j = 0, out = '', changed = false;
    const hunks = [];
    while (i < m || j < n) {
      if (i < m && j < n && A[i] === B[j]) { i++; j++; continue; }
      const si = i, sj = j;
      while ((i < m || j < n) && !(i < m && j < n && A[i] === B[j])) { if (j >= n || (i < m && L[i + 1][j] >= L[i][j + 1])) i++; else j++; }
      hunks.push([si, i, sj, j]);
    }
    const rng = (x, y) => y - x <= 1 ? String(y === x ? x : x + 1) : `${x + 1},${y}`;
    hunks.forEach(([a1, a2, b1, b2]) => {
      changed = true;
      const op = a1 === a2 ? 'a' : b1 === b2 ? 'd' : 'c';
      out += `${op === 'a' ? a1 : rng(a1, a2)}${op}${op === 'd' ? b1 : rng(b1, b2)}\n`;
      A.slice(a1, a2).forEach(l => { out += '< ' + l + '\n'; });
      if (op === 'c') out += '---\n';
      B.slice(b1, b2).forEach(l => { out += '> ' + l + '\n'; });
    });
    this.out(out);
    return changed ? 1 : 0;
  };
  C.bash = C.sh = function (a, input) {
    if (!a.length) { this.out('(a new shell would start here. In this practice shell you are already inside bash)\n'); return 0; }
    if (a[0] === '-c') { const keep = this.vars, kx = new Set(this.exported), ko = Object.assign({}, this.opts || {}), kt = this.traps; this.vars = this.childVars(); this.traps = {}; const ka = this.args; this.args = a.slice(3); try { this.runSrc(a[1] || '', true); } catch (e) { if (e && e.exit !== undefined) this.last = e.exit; else throw e; } finally { if (this.traps.EXIT) { const st = this.last; this.runTrap('EXIT'); this.last = st; } this.vars = keep; this.exported = kx; this.args = ka; this.opts = ko; this.traps = kt; } return this.last; }
    if (a[0] === '-x') { const r = this.runFileX(a[1], a.slice(2), input); return r; }
    if (a[0] !== '-n') return this.runFile(a[0], a.slice(1), input, false, true);
    const n = this.node(this.abs(a[1] || '')); if (!n) { this.eout(`bash: ${a[1]}: No such file or directory\n`); return 127; }
    try { this.parse(this.lex(n.data.replace(/(?<!<)<<(-?)\s*(['"]?)(\w+)\2([^\n]*)\n([\s\S]*?)\n\t*\3(\n|$)/g, '<<$3$4\n'))); return 0; } catch (e) { this.eout(`${a[1]}: ${e.eof ? `line ${n.data.split('\n').length}: ` : ''}${e.message}\n`); return 2; }
  };
  World.prototype.runFileX = function (path, args, input) { const p = this.abs(path), n = this.node(p); if (!n) { this.eout(`bash: ${path}: No such file or directory\n`); return 127; } const src = 'set -x\n' + n.data; const keep = n.data; n.data = src; try { return this.runFile(path, args, input, false, true); } finally { n.data = keep; } };
  C.source = C['.'] = function (a, input) { if (!a.length) { this.eout('bash: source: filename argument required\n'); return 2; } const keep = this.vars; const code = this.runFile(a[0], a.slice(1), input, false); return code; };
  C.sudo = function (a, input) {
    if (!a.length) { this.eout('usage: sudo command\n'); return 1; }
    if (a[0] === '-i' || a[0] === 'su' || a[0] === '-s') { this.user = 'root'; this.out('(you are now root. Type exit to go back to learner. Be careful, root can delete anything)\n'); return 0; }
    const keep = this.user; this.user = 'root';
    try { return this.call(a, input); } finally { this.user = keep; }
  };
  C.su = function () { this.eout('su: Authentication failure (in this practice shell use sudo instead)\n'); return 1; };
  const exitRoot = C.exit;
  C.exit = function (a) { if (this.user === 'root') { this.user = USER; return 0; } return exitRoot.call(this, a); };
  ['apt', 'dnf', 'systemctl', 'journalctl', 'ssh', 'ping', 'curl', 'wget', 'ip', 'vim', 'vi', 'nano', 'htop', 'mount', 'useradd', 'passwd', 'strace'].forEach(c => {
    C[c] = function () { this.eout(`${c}: this command is explained in its own lesson, but the practice shell does not run it. Try it on a real Linux machine, a virtual machine or WSL.\n`); return 127; };
  });
  C.vim = C.vi = C.nano = function (a) { this.eout(`${a[0] ? a[0] + ': ' : ''}the practice shell has no full screen editor. Use echo "text" > file or cat > file with a here document instead.\n`); return 1; };


  /* ---------- arrays ---------- */
  World.prototype.isAssoc = function (n) { return !!(this.assoc && this.assoc.has(n)); };
  World.prototype.arrKeys = function (n) {
    const A = this.arrays && this.arrays[n];
    if (A === undefined) return n in this.vars ? [0] : [];
    return Array.isArray(A) ? A.map((_, k) => k).filter(k => A[k] !== undefined) : Object.keys(A);
  };
  World.prototype.arrVals = function (n) {
    const A = this.arrays && this.arrays[n];
    if (A === undefined) return n in this.vars ? [this.vars[n]] : [];
    return Array.isArray(A) ? A.filter(x => x !== undefined).map(String) : Object.values(A).map(String);
  };
  World.prototype.arrGet = function (n, key, raw) {
    const A = this.arrays && this.arrays[n];
    if (this.isAssoc(n)) return (A || {})[raw ? key : this.expandStr(key)] ?? '';
    const arr = A || (n in this.vars ? [this.vars[n]] : []);
    const ix = raw ? +key : this.arith(key);
    return String(arr[ix < 0 ? arr.length + ix : ix] ?? '');
  };
  /* the words inside name=( ... ): each is expanded like a command argument. [key]=value sets one slot */
  World.prototype.arrayItems = function (inner, name) {
    const toks = this.lex(inner).filter(t => t.w);
    const out = [];
    toks.forEach(t => {
      const raw = this.wordText(t.w), m = /^\[([^\]]+)\]=(.*)$/s.exec(raw);
      if (m && !t.w.parts[0].q) { const valWord = { parts: [] }; let cut = m[1].length + 3; t.w.parts.forEach(p => { if (cut >= p.t.length) { cut -= p.t.length; return; } valWord.parts.push({ t: p.t.slice(cut), q: p.q }); cut = 0; }); out.push({ key: this.expandStr(m[1]), val: valWord.parts.length ? this.expandWord(valWord).join(' ') : '' }); return; }
      this.expandWord(t.w).forEach(v => out.push({ val: v }));
    });
    return out;
  };
  World.prototype.setArr = function (x) {
    this.arrays = this.arrays || {};
    const as = this.isAssoc(x.name);
    delete this.vars[x.name];
    if (x.list) {
      let A = x.app && this.arrays[x.name] !== undefined ? this.arrays[x.name] : as ? {} : [];
      let next = Array.isArray(A) ? A.length : 0;
      x.list.forEach(it => {
        if (as) { if (it.key === undefined) { this.eout(`bash: ${x.name}: ${it.val}: must use subscript when assigning associative array\n`); return; } A[it.key] = it.val; return; }
        if (it.key !== undefined) next = this.arith(it.key);
        A[next++] = it.val;
      });
      this.arrays[x.name] = A; return;
    }
    let A = this.arrays[x.name];
    if (A === undefined) { A = as ? {} : []; this.arrays[x.name] = A; }
    if (as) { const k = this.expandStr(x.idx); A[k] = x.app ? (A[k] || '') + x.val : x.val; return; }
    let ix = this.arith(x.idx); if (ix < 0) ix = A.length + ix;
    A[ix] = x.app ? (A[ix] || '') + x.val : x.val;
  };

  /* ---------- arithmetic: bash rules on whole numbers ---------- */
  World.prototype.arith = function (src) {
    src = String(src);
    /* inside (( )) and let, $name, ${...} and $(...) are expanded before the maths is read */
    if (src.includes('$')) src = this.expandStr(src);
    const toks = []; let i = 0;
    const OPS = ['**=', '<<=', '>>=', '&&', '||', '==', '!=', '<=', '>=', '<<', '>>', '++', '--', '+=', '-=', '*=', '/=', '%=', '&=', '^=', '|=', '**', '+', '-', '*', '/', '%', '<', '>', '=', '!', '~', '&', '^', '|', '?', ':', '(', ')', ',', '[', ']'];
    while (i < src.length) {
      const c = src[i];
      if (/\s/.test(c)) { i++; continue; }
      let m;
      if ((m = /^(0[xX][0-9a-fA-F]+|\d+#[0-9a-zA-Z@_]+|\d+)/.exec(src.slice(i)))) { toks.push({ n: m[1] }); i += m[1].length; continue; }
      if ((m = /^[A-Za-z_]\w*/.exec(src.slice(i)))) { toks.push({ id: m[0] }); i += m[0].length; continue; }
      const op = OPS.find(o => src.startsWith(o, i));
      if (!op) throw new Error(`${src.trim()}: syntax error: operand expected (error token is "${src.slice(i)}")`);
      toks.push({ op }); i += op.length;
    }
    let k = 0;
    const peek = o => toks[k] && toks[k].op === o, eat = o => { if (!peek(o)) throw new Error(`${src.trim()}: syntax error in expression (error token is "${toks[k] ? toks[k].op || toks[k].n || toks[k].id : ''}")`); k++; };
    const num = t => {
      if (/^0[xX]/.test(t)) return parseInt(t, 16);
      if (/#/.test(t)) { const [b, d] = t.split('#'); const base = +b; const dig = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@_'; let v = 0; for (const ch of d) { const x = base <= 36 ? dig.indexOf(ch.toLowerCase()) : dig.indexOf(ch); if (x < 0 || x >= base) throw new Error(`${t}: value too great for base (error token is "${t}")`); v = v * base + x; } return v; }
      if (/^0\d/.test(t)) { if (/[89]/.test(t)) throw new Error(`${t}: value too great for base (error token is "${t}")`); return parseInt(t, 8); }
      return +t;
    };
    const depth = this.arDepth = (this.arDepth || 0);
    const val = (s) => { s = String(s ?? '').trim(); if (s === '') return 0; if (/^-?\d+$/.test(s)) return +s; if (depth > 8) throw new Error('expression recursion level exceeded'); this.arDepth = depth + 1; try { return this.arith(s); } finally { this.arDepth = depth; } };
    const ref = (id, ix) => ({ get: () => val(ix === undefined ? (this.arrays && this.arrays[id] !== undefined && !(id in this.vars) ? this.arrGet(id, '0', true) : this.param(id)) : this.arrGet(id, String(ix), true)),
      set: v => { v = Math.trunc(v); if (this.ro && this.ro.has(id)) throw new Error(`${id}: readonly variable`); if (ix === undefined && !(this.arrays && this.arrays[id] !== undefined && !(id in this.vars))) this.vars[id] = String(v); else this.setArr({ name: id, idx: String(ix === undefined ? 0 : ix), val: String(v) }); return v; } });
    const T = v => Math.trunc(v);
    const comma = () => { let v = assign(); while (peek(',')) { k++; v = assign(); } return v; };
    const assign = () => {
      if (toks[k] && toks[k].id) {
        const save = k; const id = toks[k++].id; let ix;
        if (peek('[')) { k++; ix = comma(); eat(']'); }
        const t = toks[k];
        if (t && ['=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '^=', '|=', '**='].includes(t.op)) {
          k++; const r = ref(id, ix), rhs = assign(), cur = t.op === '=' ? 0 : r.get();
          if ((t.op === '/=' || t.op === '%=') && rhs === 0) throw new Error(`division by 0 (error token is "${id}")`);
          const v = { '=': rhs, '+=': cur + rhs, '-=': cur - rhs, '*=': cur * rhs, '/=': T(cur / rhs), '%=': cur % rhs, '<<=': cur << rhs, '>>=': cur >> rhs, '&=': cur & rhs, '^=': cur ^ rhs, '|=': cur | rhs, '**=': cur ** rhs }[t.op];
          return r.set(v);
        }
        k = save;
      }
      return tern();
    };
    const tern = () => { const c = bin(0); if (peek('?')) { k++; const a = comma(); eat(':'); const b = assign(); return c ? a : b; } return c; };
    const LV = [['||'], ['&&'], ['|'], ['^'], ['&'], ['==', '!='], ['<', '<=', '>', '>='], ['<<', '>>'], ['+', '-'], ['*', '/', '%']];
    const bin = lv => {
      if (lv >= LV.length) return pow();
      let l = bin(lv + 1);
      while (toks[k] && LV[lv].includes(toks[k].op)) {
        const op = toks[k++].op;
        if (op === '&&') { const r = bin(lv + 1); l = l && r ? 1 : 0; continue; }
        if (op === '||') { const r = bin(lv + 1); l = l || r ? 1 : 0; continue; }
        const r = bin(lv + 1);
        if ((op === '/' || op === '%') && r === 0) throw new Error(`${src.trim()}: division by 0 (error token is "${toks[k - 1] ? toks[k - 1].n || toks[k - 1].id || '' : ''}")`);
        l = { '|': l | r, '^': l ^ r, '&': l & r, '==': +(l === r), '!=': +(l !== r), '<': +(l < r), '<=': +(l <= r), '>': +(l > r), '>=': +(l >= r), '<<': l << r, '>>': l >> r, '+': l + r, '-': l - r, '*': l * r, '/': T(l / r), '%': l % r }[op];
      }
      return l;
    };
    const pow = () => { const b = unary(); if (peek('**')) { k++; const e = pow(); if (e < 0) throw new Error('exponent less than 0'); return b ** e; } return b; };
    const unary = () => {
      if (peek('!')) { k++; return +!unary(); }
      if (peek('~')) { k++; return ~unary(); }
      if (peek('-')) { k++; return -unary(); }
      if (peek('+')) { k++; return +unary(); }
      if (peek('++') || peek('--')) { const op = toks[k++].op; const t = toks[k++]; if (!t || !t.id) throw new Error('syntax error: operand expected'); let ix; if (peek('[')) { k++; ix = comma(); eat(']'); } const r = ref(t.id, ix); return r.set(r.get() + (op === '++' ? 1 : -1)); }
      return post();
    };
    const post = () => {
      const t = toks[k];
      if (!t) throw new Error(`${src.trim()}: syntax error: operand expected (error token is "${src.trim()}")`);
      if (t.op === '(') { k++; const v = comma(); eat(')'); return v; }
      if (t.n !== undefined) { k++; return num(t.n); }
      if (t.id) {
        k++; let ix; if (peek('[')) { k++; ix = comma(); eat(']'); }
        const r = ref(t.id, ix);
        if (peek('++') || peek('--')) { const op = toks[k++].op; const old = r.get(); r.set(old + (op === '++' ? 1 : -1)); return old; }
        return r.get();
      }
      throw new Error(`${src.trim()}: syntax error: operand expected (error token is "${t.op}${src.split(t.op).slice(1).join(t.op)}")`);
    };
    if (!toks.length) return 0;
    const v = comma();
    if (k < toks.length) { const t = toks[k]; throw new Error(`${src.trim()}: syntax error in expression (error token is "${t.op || t.n || t.id}")`); }
    return T(v);
  };

  /* ---------- [[ ... ]] ---------- */
  const PCLS = { alpha: 'a-zA-Z', digit: '0-9', alnum: 'a-zA-Z0-9', upper: 'A-Z', lower: 'a-z', space: '\\s', blank: ' \\t', punct: '!-\\/:-@\\[-`{-~', xdigit: '0-9A-Fa-f', word: '\\w' };
  const ereToJs = re => re.replace(/\[:(\w+):\]/g, (m, n) => PCLS[n] || m);
  /* a glob pattern for [[ == ]]: * and ? match / too, quoted parts are literal */
  const patRe = parts => {
    let r = '';
    parts.forEach(([t, lit]) => {
      if (lit) { r += t.replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&'); return; }
      for (let i = 0; i < t.length; i++) {
        const c = t[i];
        if (c === '\\' && i + 1 < t.length) { r += t[++i].replace(/[.*+?^${}()|[\]\\\/]/g, '\\$&'); continue; }
        if (c === '*') r += '[\\s\\S]*'; else if (c === '?') r += '[\\s\\S]';
        else if (c === '[') { const j = t.indexOf(']', i + 2); if (j < 0) { r += '\\['; continue; } let set = t.slice(i + 1, j); if (set[0] === '!') set = '^' + set.slice(1); r += '[' + ereToJs(set).replace(/\\(?![sdtw])/g, '\\\\') + ']'; i = j; }
        else r += c.replace(/[.+^${}()|\\\/]/g, '\\$&');
      }
    });
    return new RegExp('^' + r + '$');
  };
  World.prototype.dbl = function (text) {
    const regs = [];
    /* the right side of =~ is taken raw up to the first space outside quotes and brackets */
    text = text.replace(/=~\s*/g, '=~ ').replace(/(=~ )((?:\\.|'[^']*'|"(?:\\.|[^"\\])*"|\([^)]*\)|[^\s])+)/g, (all, op, re) => { regs.push(re); return op + '__RE' + (regs.length - 1) + '__'; });
    let toks;
    try { toks = this.lex(text); } catch (e) { this.eout(`bash: ${e.message}\n`); return 2; }
    let k = 0;
    const W = () => toks[k] && toks[k].w ? toks[k].w : null;
    const raw = w => this.wordText(w);
    const isW = s => W() && !W().parts.some(p => p.q) && raw(W()) === s;
    const val = w => { let v = w.parts.map(p => p.q === 1 ? p.t : this.expandStr(p.t)).join(''); if (!w.parts[0].q && (v === '~' || v.startsWith('~/'))) v = HOME + v.slice(1); return v; };
    const regex = idx => {
      const r = regs[idx]; let out = '';
      for (let i = 0; i < r.length; i++) {
        const c = r[i];
        if (c === "'") { const j = r.indexOf("'", i + 1); out += r.slice(i + 1, j).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); i = j; continue; }
        if (c === '"') { let j = i + 1, s = ''; while (j < r.length && r[j] !== '"') { if (r[j] === '\\' && '"\\$'.includes(r[j + 1])) { s += r[j + 1]; j += 2; continue; } s += r[j++]; } out += this.expandStr(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); i = j; continue; }
        if (c === '$') { const m = /^\$(\{[^}]+\}|\w+)/.exec(r.slice(i)); if (m) { out += this.expandStr(m[0]); i += m[0].length - 1; continue; } }
        out += c;
      }
      return ereToJs(out);
    };
    const N = v => { try { return this.arith(v); } catch (e) { throw new Error(e.message); } };
    const prim = () => {
      if (toks[k] && toks[k].op === '(') { k++; const v = orE(); if (!(toks[k] && toks[k].op === ')')) throw new Error('syntax error in conditional expression: expected )'); k++; return v; }
      if (isW('!')) { k++; return !prim(); }
      const w = W();
      if (!w) throw new Error(`syntax error in conditional expression${toks[k] ? ` near "${toks[k].op}"` : ''}`);
      const r0 = raw(w);
      if (/^-[a-zA-Z]$/.test(r0) && !w.parts[0].q && toks[k + 1] && toks[k + 1].w && !(toks[k + 2] && toks[k + 2].w && /^(==?|!=|=~|-eq|-ne|-lt|-le|-gt|-ge|-nt|-ot|-ef)$/.test(raw(toks[k + 2].w)))) {
        k++; const x = val(W()); k++;
        const ft = this.fileTest(r0, x);
        if (ft !== undefined) return ft;
        switch (r0) {
          case '-v': { const m = /^(\w+)(?:\[(.+)\])?$/.exec(x); if (!m) return false; if (m[2] !== undefined) return this.arrKeys(m[1]).map(String).includes(this.isAssoc(m[1]) ? this.expandStr(m[2]) : String(this.arith(m[2]))); return m[1] in this.vars || !!(this.arrays && this.arrays[m[1]] !== undefined); }
          case '-o': return !!(this.opts && this.opts[x]);
        }
        throw new Error(`${r0}: unary operator expected`);
      }
      k++;
      const opTok = toks[k];
      const op = opTok && opTok.w && !opTok.w.parts.some(p => p.q) ? raw(opTok.w) : opTok && (opTok.op === '<' || opTok.op === '>') ? opTok.op : null;
      if (op && ['==', '=', '!=', '=~', '<', '>', '-eq', '-ne', '-lt', '-le', '-gt', '-ge', '-nt', '-ot', '-ef'].includes(op)) {
        k++; const rw = W(); if (!rw) throw new Error(`unexpected argument to conditional binary operator`); k++;
        const l = val(w);
        if (op === '=~') {
          const m = /^__RE(\d+)__$/.exec(raw(rw)); const re = m ? regex(+m[1]) : val(rw);
          let R; try { R = new RegExp(re); } catch (e) { this.regBad = true; return false; }
          const hit = R.exec(l); this.arrays = this.arrays || {}; this.arrays.BASH_REMATCH = hit ? hit.map(x => x ?? '') : [];
          return !!hit;
        }
        if (op === '==' || op === '=' || op === '!=') { let pr = patRe(rw.parts.map(p => [p.q === 1 ? p.t : this.expandStr(p.t), !!p.q])); if (this.shopt('nocasematch')) pr = new RegExp(pr.source, 'i'); return op === '!=' ? !pr.test(l) : pr.test(l); }
        const r = val(rw);
        switch (op) {
          case '<': return l < r; case '>': return l > r;
          case '-eq': return N(l) === N(r); case '-ne': return N(l) !== N(r); case '-lt': return N(l) < N(r);
          case '-le': return N(l) <= N(r); case '-gt': return N(l) > N(r); case '-ge': return N(l) >= N(r);
          case '-nt': case '-ot': case '-ef': return this.fileCmp(op, l, r);
        }
      }
      return val(w) !== '';
    };
    const andE = () => { let v = prim(); while (toks[k] && toks[k].op === '&&') { k++; const r = prim(); v = v && r; } return v; };
    const orE = () => { let v = andE(); while (toks[k] && toks[k].op === '||') { k++; const r = andE(); v = v || r; } return v; };
    this.regBad = false;
    try {
      const v = orE();
      if (k < toks.length) throw new Error(`syntax error in conditional expression near "${toks[k].op || raw(toks[k].w)}"`);
      return this.regBad ? 2 : v ? 0 : 1;
    } catch (e) { this.eout(`bash: ${e.message}\n`); return e.message.includes('syntax') ? 2 : 1; }
  };

  /* ---------- traps ---------- */
  World.prototype.runTrap = function (sig) {
    const cmd = this.traps && this.traps[sig];
    if (!cmd) return;
    this.inTrap = true;
    try { this.runSrc(cmd, true); } catch (e) { if (!(e && e.exit !== undefined)) throw e; } finally { this.inTrap = false; }
  };
  C.trap = function (a) {
    this.traps = this.traps || {};
    if (!a.length || a[0] === '-p') { Object.keys(this.traps).forEach(k => { if (this.traps[k] !== undefined) this.out(`trap -- '${this.traps[k].replace(/'/g, "'\\''")}' ${k}\n`); }); return 0; }
    if (a[0] === '-l') return C.kill.call(this, ['-l']);
    const [cmd, ...sigs] = a;
    if (!sigs.length) { this.eout('trap: usage: trap [-lp] [[arg] signal_spec ...]\n'); return 2; }
    let code = 0;
    sigs.forEach(s0 => {
      const s = String(s0).toUpperCase().replace(/^SIG/, '');
      const name = s === '0' ? 'EXIT' : ['EXIT', 'ERR', 'DEBUG', 'RETURN'].includes(s) ? s : sigNum(s) > 0 ? sigName(sigNum(s)) : null;
      if (!name) { this.eout(`bash: trap: ${s0}: invalid signal specification\n`); code = 1; return; }
      if (cmd === '-') delete this.traps[name]; else this.traps[name] = cmd;
    });
    return code;
  };

  /* ---------- small builtins for scripts ---------- */
  C[':'] = function () { return 0; };
  /* ---------- cron and at ---------- */
  /* one crontab line: '' when fine, else the reason, using the words of the cron man pages */
  const CRON_AT = ['@reboot', '@yearly', '@annually', '@monthly', '@weekly', '@daily', '@midnight', '@hourly'];
  World.prototype.cronCheck = function (line) {
    const t = line.trim();
    if (!t || t.startsWith('#') || /^[A-Za-z_]\w*\s*=/.test(t)) return '';
    const f = t.split(/\s+/);
    if (f[0].startsWith('@')) return CRON_AT.includes(f[0]) ? (f.length > 1 ? '' : 'missing command') : 'bad time specifier';
    if (f.length < 6) return f.length < 5 ? ['bad minute', 'bad hour', 'bad day-of-month', 'bad month', 'bad day-of-week'][f.length] || 'bad minute' : 'missing command';
    const names = { 3: 'jan feb mar apr may jun jul aug sep oct nov dec'.split(' '), 4: 'sun mon tue wed thu fri sat'.split(' ') };
    const lim = [[0, 59], [0, 23], [1, 31], [1, 12], [0, 7]], what = ['minute', 'hour', 'day-of-month', 'month', 'day-of-week'];
    for (let k = 0; k < 5; k++) {
      const ok = f[k].split(',').every(part => {
        const m = /^(\*|([0-9a-z]+)(?:-([0-9a-z]+))?)(?:\/(\d+))?$/i.exec(part);
        if (!m) return false;
        const num = x => { if (/^\d+$/.test(x)) return +x; const n = names[k] && names[k].indexOf(x.toLowerCase()); return n >= 0 ? n + (k === 3 ? 1 : 0) : NaN; };
        if (m[1] === '*') return !m[4] || +m[4] > 0;
        const a = num(m[2]), b = m[3] !== undefined ? num(m[3]) : a;
        return a >= lim[k][0] && b <= lim[k][1] && a <= b && !(m[4] && +m[4] === 0);
      });
      if (!ok) return 'bad ' + what[k];
    }
    return '';
  };
  C.crontab = function (a, input) {
    const user = (a[0] === '-u' && a[1]) ? a[1] : this.user;
    if (a[0] === '-u') { if (this.user !== 'root') { this.eout('must be privileged to use -u\n'); return 1; } a = a.slice(2); }
    const spool = '/var/spool/cron/crontabs', path = spool + '/' + user, have = this.node(path);
    if (a[0] === '-l') { if (!have) { this.eout(`no crontab for ${user}\n`); return 1; } this.out(have.data); return 0; }
    if (a[0] === '-r') { if (!have) { this.eout(`no crontab for ${user}\n`); return 1; } this.removeNode(path); return 0; }
    if (a[0] === '-e') { this.eout('crontab -e opens your editor ($EDITOR), and the practice shell has no full-screen editor. Write the lines into a file and install it with: crontab FILE\n'); return 1; }
    if (!a.length) { this.eout('usage:\tcrontab [-u user] file\n\tcrontab [-u user] { -e | -l | -r }\n'); return 1; }
    const src = a[0] === '-' ? input : (() => { const n = this.node(this.abs(a[0])); return n ? n.data : null; })();
    if (src === null) { this.eout(`${a[0]}: No such file or directory\n`); return 1; }
    const bad = src.split('\n').map((l, i) => [i + 1, this.cronCheck(l)]).find(([, e]) => e);
    if (bad) { this.eout(`"${a[0] === '-' ? '-' : a[0]}":${bad[0]}: ${bad[1]}\nerrors in crontab file, can't install.\n`); return 1; }
    this.mkdirs(spool);
    const n = this.node(path) || this.mk(path, 'f', 0o600, user, ''); n.group = 'crontab';
    n.data = src.endsWith('\n') || !src ? src : src + '\n'; n.mtime = this.now();
    return 0;
  };
  /* at: run commands once, later. Times: now + N minutes|hours|days, HH:MM, noon, midnight, teatime, optional tomorrow */
  const DAYS3 = 'Sun Mon Tue Wed Thu Fri Sat'.split(' '), MON3 = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ');
  const atDate = ms => { const d = new Date(ms), z = n => String(n).padStart(2, '0'); return `${DAYS3[d.getUTCDay()]} ${MON3[d.getUTCMonth()]} ${String(d.getUTCDate()).padStart(2, ' ')} ${z(d.getUTCHours())}:${z(d.getUTCMinutes())}:00 ${d.getUTCFullYear()}`; };
  World.prototype.atTime = function (words) {
    const t = words.join(' ').toLowerCase().trim(), now = this.clock - this.clock % 60000;
    let m;
    if ((m = /^now(?:\s*\+\s*(\d+)\s*(minute|min|hour|day|week)s?)?$/.exec(t))) return now + (m[1] ? +m[1] * { minute: 6e4, min: 6e4, hour: 36e5, day: 864e5, week: 6048e5 }[m[2]] : 0);
    if ((m = /^(noon|midnight|teatime|(\d{1,2}):(\d{2})\s*(am|pm)?|(\d{1,2})\s*(am|pm))(\s+tomorrow)?$/.exec(t))) {
      let h, mi = 0;
      if (m[1] === 'noon') h = 12; else if (m[1] === 'midnight') h = 0; else if (m[1] === 'teatime') h = 16;
      else if (m[2] !== undefined) { h = +m[2]; mi = +m[3]; if (m[4] === 'pm' && h < 12) h += 12; if (m[4] === 'am' && h === 12) h = 0; }
      else { h = +m[5]; if (m[6] === 'pm' && h < 12) h += 12; if (m[6] === 'am' && h === 12) h = 0; }
      if (h > 23 || mi > 59) return null;
      const d = new Date(now); let when = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(), h, mi);
      if (m[7]) when += 864e5; else if (when <= now) when += 864e5;
      return when;
    }
    return null;
  };
  C.at = function (a, input) {
    if (a[0] === '-l') return C.atq.call(this, a.slice(1));
    if (a[0] === '-r' || a[0] === '-d') return C.atrm.call(this, a.slice(1));
    let file = null; if (a[0] === '-f') { file = a[1]; a = a.slice(2); }
    if (!a.length) { this.eout('Garbled time\n'); return 1; }
    const when = this.atTime(a);
    if (when === null) { this.eout('syntax error. Last token seen: ' + a[a.length - 1] + '\nGarbled time\n'); return 1; }
    let body = input || '';
    if (file) { const n = this.node(this.abs(file)); if (!n) { this.eout(`Cannot open input file ${file}: No such file or directory\n`); return 1; } body = n.data; }
    this.atjobs = this.atjobs || []; this.atNext = (this.atNext || 0) + 1;
    this.atjobs.push({ id: this.atNext, when, user: this.user, body });
    this.eout(`warning: commands will be executed using /bin/sh\njob ${this.atNext} at ${atDate(when)}\n`);
    return 0;
  };
  C.batch = function (a, input) { return C.at.call(this, ['now'], input); };
  C.atq = function () { (this.atjobs || []).slice().sort((x, y) => x.when - y.when).forEach(j => this.out(`${j.id}\t${atDate(j.when)} a ${j.user}\n`)); return 0; };
  C.atrm = function (a) {
    let code = 0;
    a.forEach(id => { const k = (this.atjobs || []).findIndex(j => String(j.id) === id); if (k < 0) { this.eout(`Cannot find jobid ${id}\n`); code = 1; } else this.atjobs.splice(k, 1); });
    return code;
  };
  /* command -v NAME tells where a command comes from, command NAME ... runs it without looking at functions */
  C.command = function (a, input) {
    if (a[0] === '-v' || a[0] === '-V') {
      let code = 0;
      a.slice(1).forEach(n => {
        if (this.aliases && this.aliases[n]) this.out(a[0] === '-v' ? `alias ${n}='${this.aliases[n]}'\n` : `${n} is aliased to \`${this.aliases[n]}'\n`);
        else if (this.fns && this.fns[n]) this.out(a[0] === '-v' ? n + '\n' : `${n} is a function\n`);
        else if (BUILTIN.has(n)) this.out(a[0] === '-v' ? n + '\n' : `${n} is a shell builtin\n`);
        else { const hit = this.lookup(n); if (hit) this.out(a[0] === '-v' ? hit.path + '\n' : `${n} is ${hit.path}\n`); else { if (a[0] === '-V') this.eout(`bash: command: ${n}: not found\n`); code = 1; } }
      });
      return code;
    }
    if (!a.length) return 0;
    const keep = this.fns; this.fns = {};
    try { return this.call(a, input); } finally { this.fns = keep; }
  };
  /* flock [-n] [-w SECONDS] FILE COMMAND ...: run COMMAND holding a lock on FILE. One user, so the lock is always free */
  C.flock = function (a, input) {
    let i = 0;
    while (/^-[nwxsoeu]/.test(a[i] || '')) { if (a[i] === '-w') i++; i++; }
    const file = a[i], cmd = a.slice(i + 1);
    if (!file) { this.eout('flock: bad usage\nTry \'flock --help\' for more information.\n'); return 64; }
    if (/^\d+$/.test(file)) { this.eout('flock: file descriptors are not available in the practice shell, use flock FILE COMMAND\n'); return 64; }
    const p = this.abs(file);
    if (!this.node(p)) { if (!this.node(dirName(p))) { this.eout(`flock: cannot open lock file ${file}: No such file or directory\n`); return 66; } this.mk(p, 'f', 0o644, this.user, ''); }
    return cmd.length ? this.call(cmd, input) : 0;
  };
  /* shopt: the bash options that change globbing and matching */
  const SHOPTS = ['dotglob', 'expand_aliases', 'extglob', 'failglob', 'globstar', 'nocaseglob', 'nocasematch', 'nullglob'];
  C.shopt = function (a) {
    const on = this.shopts = this.shopts || new Set(['expand_aliases', 'extglob']);
    let mode = '', q = false; const names = [];
    a.forEach(x => { if (x === '-s' || x === '-u') mode = x; else if (x === '-q') q = true; else names.push(x); });
    const bad = names.find(n => !SHOPTS.includes(n));
    if (bad) { this.eout(`bash: shopt: ${bad}: invalid shell option name\n`); return 1; }
    if (mode) { names.forEach(n => mode === '-s' ? on.add(n) : on.delete(n)); return 0; }
    const list = names.length ? names : SHOPTS;
    if (!q) list.forEach(n => this.out(`${n.padEnd(15)}\t${on.has(n) ? 'on' : 'off'}\n`));
    return list.every(n => on.has(n)) ? 0 : 1;
  };
  World.prototype.shopt = function (n) { return !!(this.shopts && this.shopts.has(n)); };
  C.eval = function (a) { if (!a.length) return 0; this.runSrc(a.join(' '), true); return this.last; };
  C.shift = function (a) { const n = a.length ? +a[0] : 1; if (!(n >= 0) || n > this.args.length) { if (a.length) this.eout(`bash: shift: ${a[0]}: shift count out of range\n`); return 1; } this.args = this.args.slice(n); return 0; };
  C.let = function (a) { if (!a.length) { this.eout('bash: let: expression expected\n'); return 1; } let v = 0; try { a.forEach(x => { v = this.arith(x); }); } catch (e) { this.eout(`bash: let: ${e.message}\n`); return 1; } return v ? 0 : 1; };
  C.local = function (a) {
    const fr = this.frames && this.frames[this.frames.length - 1];
    if (!fr) { this.eout('bash: local: can only be used in a function\n'); return 1; }
    a.filter(x => !/^[-+][a-zA-Z]+$/.test(x)).forEach(x => {
      const k = /^\w+/.exec(x)[0];
      if (fr.some(f => f[0] === k)) return;
      const A = this.arrays && this.arrays[k];
      fr.push([k, k in this.vars, this.vars[k], A !== undefined, A === undefined ? undefined : Array.isArray(A) ? A.slice() : Object.assign({}, A), this.isAssoc(k)]);
      if (!x.includes('=')) { delete this.vars[k]; if (this.arrays) delete this.arrays[k]; if (this.assoc) this.assoc.delete(k); }
    });
    return C.declare.call(this, a.map(x => x.includes('=') || /^[-+]/.test(x) ? x : x));
  };
  C.mapfile = C.readarray = function (a, input) {
    const [f, rest] = opts(a, 'nsu');
    const name = rest[0] || 'MAPFILE';
    let ls = (input || '').split('\n'); if (ls[ls.length - 1] === '') ls.pop();
    if (f.s) ls = ls.slice(+f.s); if (f.n && +f.n) ls = ls.slice(0, +f.n);
    (this.arrays = this.arrays || {})[name] = ls.map(l => f.t ? l : l + '\n');
    if (this.assoc) this.assoc.delete(name); delete this.vars[name];
    return 0;
  };
  C.getopts = function (a) {
    if (a.length < 2) { this.eout('getopts: usage: getopts optstring name [arg ...]\n'); return 2; }
    const [spec0, name] = a, args = a.length > 2 ? a.slice(2) : this.args;
    const silent = spec0.startsWith(':'), spec = silent ? spec0.slice(1) : spec0;
    let ind = +(this.vars.OPTIND || 1); if (ind !== this.optLastInd) this.optPos = 1;
    const arg = args[ind - 1];
    if (arg === undefined || arg === '--' || !/^-./.test(arg)) { this.vars.OPTIND = String(arg === '--' ? ind + 1 : ind); this.vars[name] = '?'; delete this.vars.OPTARG; this.optLastInd = undefined; return 1; }
    const ch = arg[this.optPos], at = spec.indexOf(ch);
    const step = () => { this.optPos++; if (this.optPos >= arg.length) { ind++; this.optPos = 1; } this.vars.OPTIND = String(ind); this.optLastInd = ind; };
    if (at < 0 || ch === ':') { step(); if (silent) { this.vars[name] = '?'; this.vars.OPTARG = ch; } else { this.eout(`${this.script || 'bash'}: illegal option -- ${ch}\n`); this.vars[name] = '?'; delete this.vars.OPTARG; } return 0; }
    if (spec[at + 1] === ':') {
      let val = arg.slice(this.optPos + 1);
      if (val) { ind++; } else { val = args[ind]; ind += val === undefined ? 1 : 2; }
      this.optPos = 1; this.vars.OPTIND = String(ind); this.optLastInd = ind;
      if (val === undefined) { if (silent) { this.vars[name] = ':'; this.vars.OPTARG = ch; } else { this.eout(`${this.script || 'bash'}: option requires an argument -- ${ch}\n`); this.vars[name] = '?'; delete this.vars.OPTARG; } return 0; }
      this.vars[name] = ch; this.vars.OPTARG = val; return 0;
    }
    step(); this.vars[name] = ch; delete this.vars.OPTARG; return 0;
  };
  C.mktemp = function (a) {
    const [f, rest] = opts(a, 'p');
    const AL = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let tpl = rest[0] || 'tmp.XXXXXXXXXX'; const m = /X{3,}$/.exec(tpl);
    if (!m) { this.eout(`mktemp: too few X's in template '${tpl}'\n`); return 1; }
    tpl = tpl.slice(0, m.index) + Array.from({ length: m[0].length }, () => AL[Math.floor(Math.random() * AL.length)]).join('');
    const p = tpl.includes('/') ? this.abs(tpl) : norm((f.p || this.vars.TMPDIR || '/tmp') + '/' + tpl);
    if (f.u) { this.out(p + '\n'); return 0; }
    this.mk(p, f.d ? 'd' : 'f', f.d ? 0o700 : 0o600, this.user, '').mtime = this.now();
    this.out(p + '\n'); return 0;
  };

  /* ---------- checking missions ---------- */
  function check(w, conds, last) {
    return (conds || []).every(c => {
      if (c.cmd) return new RegExp(c.cmd).test(last.cmd || '');
      if (c.out) return new RegExp(c.out, 'm').test(last.out || '');
      if (c.code !== undefined) return last.code === c.code;
      if (c.cwd) return w.cwd === w.abs(c.cwd);
      if (c.exists) { const n = w.node(w.abs(c.exists), c.type !== 'l'); return !!n && (!c.type || n.type === c.type); }
      if (c.gone) return !w.node(w.abs(c.gone), false);
      if (c.has) { const n = w.node(w.abs(c.has[0])); return !!n && n.type === 'f' && n.data.includes(c.has[1]); }
      if (c.mode) { const n = w.node(w.abs(c.mode[0])); return !!n && (n.mode & 0o7777).toString(8) === String(c.mode[1]).replace(/^0+(?=.)/, ''); }
      if (c.lines) { const n = w.node(w.abs(c.lines[0])); return !!n && lines(n.data).length === c.lines[1]; }
      if (c.env) return w.vars[c.env[0]] === c.env[1];
      if (c.envre) return new RegExp(c.envre[1]).test(w.vars[c.envre[0]] ?? '');
      if (c.exported) return w.exported.has(c.exported);
      if (c.alias) return w.aliases[c.alias[0]] === c.alias[1];
      if (c.owner) { const n = w.node(w.abs(c.owner[0])); return !!n && n.owner === c.owner[1]; }
      return false;
    });
  }

  /* ---------- the terminal on the page ---------- */
  const esc = s => String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
  function colourLs(w, text, cmd) {
    if (!/^\s*(ls|ll|la)\b/.test(cmd) || /\|/.test(cmd)) return esc(text);
    return text.split('\n').map(line => {
      const m = /^([dlc-][rwxstST-]{9})(.*\s)(\S+)( -> .*)?$/.exec(line);
      if (m) { const cls = m[1][0] === 'd' ? 'lx-d' : m[1][0] === 'l' ? 'lx-l' : /x/.test(m[1]) ? 'lx-x' : ''; return esc(m[1] + m[2]) + (cls ? `<span class="${cls}">${esc(m[3])}</span>` : esc(m[3])) + esc(m[4] || ''); }
      if (/^total \d+$|:$/.test(line)) return esc(line);
      return line.split(/(\s{2,})/).map(tok => {
        if (/^\s+$/.test(tok) || !tok) return tok;
        const n = w.node(w.abs(tok), false) || w.node(w.abs(tok));
        if (!n) return esc(tok);
        return n.type === 'd' ? `<span class="lx-d">${esc(tok)}</span>` : n.type === 'l' ? `<span class="lx-l">${esc(tok)}</span>` : (n.mode & 0o111) ? `<span class="lx-x">${esc(tok)}</span>` : esc(tok);
      }).join('');
    }).join('\n');
  }
  function treeHtml(w) {
    const walk = (n, path, depth) => Object.keys(n.kids).sort().filter(k => !k.startsWith('.')).map(k => {
      const c = n.kids[k], p = path + '/' + k, here = w.cwd === p;
      const icon = c.type === 'd' ? '📁' : c.type === 'l' ? '🔗' : (c.mode & 0o111) ? '⚙️' : '📄';
      const kids = c.type === 'd' && depth < 3 ? walk(c, p, depth + 1) : '';
      return `<li class="${here ? 'here' : ''}"><span>${icon} ${esc(k)}</span>${kids ? `<ul>${kids}</ul>` : ''}</li>`;
    }).join('');
    const home = w.node(HOME);
    return `<div class="lx-tree-h">Your files in ${esc(w.tilde(HOME))}</div><ul class="lx-tree-r"><li class="${w.cwd === HOME ? 'here' : ''}"><span>🏠 ~</span><ul>${walk(home, HOME, 1)}</ul></li></ul>`;
  }
  function mount(el) {
    if (el.dataset.on) return;
    el.dataset.on = '1';
    let lab = {};
    try { lab = JSON.parse(el.dataset.lab || '{}'); } catch (e) { /* bad lab, use the default world */ }
    const fresh = el.cloneNode(true);
    let w = new World(lab);
    const missions = lab.missions || [];
    const done = missions.map(() => false);
    el.innerHTML = `<div class="lx-head"><span class="lx-dots"><i></i><i></i><i></i></span><b>${esc(lab.title || 'Practice shell')}</b><span class="lx-sub">A pretend Linux in your browser. Nothing you type can harm your computer.</span>
        <span class="lx-btns"><button type="button" class="lx-files">Show my files</button><button type="button" class="lx-reset" title="Start again with fresh files">↺ Reset</button></span></div>
      <div class="lx-main"><div class="lx-screen" tabindex="0" aria-label="Terminal"><div class="lx-out" aria-live="polite"></div>
        <div class="lx-line"><span class="lx-ps"></span><input class="lx-in" type="text" spellcheck="false" autocomplete="off" autocapitalize="off" aria-label="Type a command and press Enter"></div></div>
        <aside class="lx-side" hidden></aside></div>
      ${missions.length ? `<div class="lx-ms"><div class="lx-ms-h"><b>Missions</b><span class="lx-score">0 of ${missions.length} done</span></div><ol>${missions.map((m, i) => `<li data-i="${i}"><span class="lx-tick" aria-hidden="true"></span><span class="lx-t">${m.t}</span><button type="button" class="lx-hint" data-i="${i}">Hint</button><code class="lx-hv" hidden>${esc(m.hint || '')}</code></li>`).join('')}</ol></div>` : ''}
      <div class="lx-keys">Enter runs a command. Up and Down bring back earlier commands. Tab completes a name. Type <code>help</code> to see every command, <code>clear</code> to clean the screen.</div>`;
    const out = el.querySelector('.lx-out'), inp = el.querySelector('.lx-in'), ps = el.querySelector('.lx-ps'), side = el.querySelector('.lx-side'), scr = el.querySelector('.lx-screen');
    let hi = 0;
    const psHtml = () => { const p = w.prompt(); return `<span class="lx-u">${esc(p.user)}@${p.host}</span>:<span class="lx-p">${esc(p.dir)}</span>${p.sign} `; };
    const paint = () => { ps.innerHTML = psHtml(); if (!side.hidden) side.innerHTML = treeHtml(w); };
    const print = (html) => { const d = document.createElement('div'); d.innerHTML = html; out.appendChild(d); while (out.childNodes.length > 400) out.removeChild(out.firstChild); scr.scrollTop = scr.scrollHeight; };
    print(`<span class="lx-dim">Welcome to the practice shell. You are <b>${USER}</b> on the computer <b>${HOST}</b>. Try <code>ls</code> or <code>pwd</code>.</span>`);
    paint();
    const score = () => { const s = el.querySelector('.lx-score'); if (s) s.textContent = `${done.filter(Boolean).length} of ${missions.length} done`; };
    function runLine(line) {
      print(psHtml() + esc(line));
      const r = w.run(line);
      if (w.cleared) { out.innerHTML = ''; w.cleared = false; }
      if (r.out) print(colourLs(w, r.out.replace(/\n$/, ''), line));
      const last = { cmd: line, out: r.out, code: r.code };
      missions.forEach((m, i) => {
        if (done[i] || !check(w, m.check, last)) return;
        done[i] = true;
        const li = el.querySelector(`.lx-ms li[data-i="${i}"]`);
        if (li) { li.classList.add('ok'); li.animate && li.animate([{ transform: 'scale(1)' }, { transform: 'scale(1.03)' }, { transform: 'scale(1)' }], { duration: 500 }); }
        print(`<span class="lx-win">✔ Mission ${i + 1} done: ${m.t.replace(/<[^>]+>/g, '')}</span>`);
        score();
        if (done.every(Boolean)) print('<span class="lx-win">🎉 Every mission is done. Brilliant work. Keep exploring, or press Reset to start again.</span>');
      });
      paint();
    }
    inp.addEventListener('keydown', e => {
      if (e.key === 'Enter') { const v = inp.value; inp.value = ''; hi = w.hist.length + 1; runLine(v); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { if (w.hist.length) { hi = Math.max(0, (hi || w.hist.length) - 1); inp.value = w.hist[hi] || ''; } e.preventDefault(); }
      else if (e.key === 'ArrowDown') { hi = Math.min(w.hist.length, hi + 1); inp.value = w.hist[hi] || ''; e.preventDefault(); }
      else if (e.key === 'Tab') {
        e.preventDefault();
        const v = inp.value, m = /(\S*)$/.exec(v), word = m[1], first = !/\s/.test(v.trim()) && !v.endsWith(' ');
        let opts2 = [];
        if (first) opts2 = Object.keys(C).filter(c => c.startsWith(word) && c.length > 1);
        else { const dir = word.includes('/') ? word.slice(0, word.lastIndexOf('/') + 1) : '', base = word.slice(dir.length), n = w.node(w.abs(dir || '.')); if (n && n.type === 'd') opts2 = Object.keys(n.kids).filter(k => k.startsWith(base) && (base.startsWith('.') || !k.startsWith('.'))).map(k => dir + k + (n.kids[k].type === 'd' ? '/' : '')); }
        if (opts2.length === 1) inp.value = v.slice(0, v.length - word.length) + opts2[0] + (opts2[0].endsWith('/') ? '' : ' ');
        else if (opts2.length > 1) { let p = opts2[0]; opts2.forEach(o => { while (!o.startsWith(p)) p = p.slice(0, -1); }); if (p.length > word.length) inp.value = v.slice(0, v.length - word.length) + p; else print(esc(opts2.join('  '))); }
      } else if (e.key === 'l' && e.ctrlKey) { out.innerHTML = ''; e.preventDefault(); }
      else if (e.key === 'c' && e.ctrlKey && !getSelection().toString()) { print(psHtml() + esc(inp.value) + '^C'); inp.value = ''; e.preventDefault(); }
    });
    scr.addEventListener('click', () => { if (!getSelection().toString()) inp.focus({ preventScroll: true }); });
    el.querySelector('.lx-files').addEventListener('click', e => { side.hidden = !side.hidden; e.target.textContent = side.hidden ? 'Show my files' : 'Hide my files'; paint(); });
    el.querySelector('.lx-reset').addEventListener('click', () => { const n = fresh.cloneNode(true); el.replaceWith(n); mount(n); });
    el.querySelectorAll('.lx-hint').forEach(b => b.addEventListener('click', () => { const c = b.nextElementSibling; c.hidden = !c.hidden; b.textContent = c.hidden ? 'Hint' : 'Hide'; }));
    el.querySelectorAll('.lx-hv').forEach(c => c.addEventListener('click', () => { inp.value = c.textContent; inp.focus(); }));
  }
  function mountAll(root = document) { root.querySelectorAll('.lx-term').forEach(mount); }
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => mountAll()); else mountAll();
  }
  return { World, mount, mountAll, check, SEED, HOME, USER, toRe };
})();
if (typeof module !== 'undefined') module.exports = LXSH;
