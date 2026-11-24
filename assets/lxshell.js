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
    dirs: [['/bin', 0o755, 'root'], ['/boot', 0o755, 'root'], ['/dev', 0o755, 'root'], ['/etc', 0o755, 'root'], ['/etc/skel', 0o755, 'root'], ['/home', 0o755, 'root'],
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
      ['/etc/group', 'root:x:0:\nadm:x:4:\nsudo:x:27:learner\nwww-data:x:33:\nlearner:x:1000:\nasha:x:1001:\n', 0o644, 'root'],
      ['/etc/shadow', 'root:*:20415:0:99999:7:::\nlearner:$y$j9T$demo$demo:20415:0:99999:7:::\n', 0o640, 'root'],
      ['/etc/skel/.bashrc', '# ~/.bashrc: executed by bash(1) for non-login shells.\n', 0o644, 'root'],
      ['/etc/skel/.profile', '# ~/.profile: executed by the command interpreter for login shells.\n', 0o644, 'root'],
      ['/etc/skel/.bash_logout', '# ~/.bash_logout: executed by bash(1) when login shell exits.\n', 0o644, 'root'],
      ['/etc/hosts', '127.0.0.1 localhost\n127.0.1.1 brainy\n', 0o644, 'root'],
      ['/etc/fstab', '# <file system> <mount point> <type> <options> <dump> <pass>\nUUID=b6e1c2a4-77aa-4e0f-9d3b-2f1c8a5e0d71 / ext4 errors=remount-ro 0 1\n', 0o644, 'root'],
      ['/var/log/syslog', 'Nov 23 09:00:00 brainy systemd[1]: Started Daily apt download activities.\nNov 23 09:00:02 brainy CRON[812]: (root) CMD (run-parts /etc/cron.hourly)\n', 0o640, 'root'],
      ['/proc/version', 'Linux version 6.8.0-practice (practice@brainy) #1 SMP\n', 0o444, 'root'],
      ['/proc/cpuinfo', 'processor\t: 0\nmodel name\t: Practice CPU\ncpu cores\t: 2\nprocessor\t: 1\nmodel name\t: Practice CPU\ncpu cores\t: 2\n', 0o444, 'root'],
      ['/var/www/index.html', '<h1>It works</h1>\n', 0o644, 'root']
    ]
  };
  const PKGCMDS = ['cowsay', 'jq', 'figlet'];
  const SBIN = 'setcap ufw sshd tcpdump pvcreate pvs pvremove vgcreate vgextend vgs vgremove lvcreate lvextend lvreduce lvresize lvs lvremove mkswap swapon swapoff mkfs mkfs.ext4 mkfs.xfs mkfs.vfat parted e2fsck chpasswd groupadd groupdel useradd userdel usermod'.split(' ');
  const CMDS = 'vmstat iostat mpstat pidstat capsh getcap sysctl mkfifo nproc pstree alias blkid fallocate scp ssh ssh-copy-id ssh-keygen curl dig host ip nc nslookup ping ss tracepath traceroute findmnt fsck lsblk mount umount dmesg logger journalctl systemctl apt apt-cache apt-get at atq atrm awk basename bash batch bg bunzip2 bzcat bzip2 cal cat cd chage chmod chown clear cp crontab cut date df diff dpkg dpkg-query dirname disown du echo env exit export expr false fg file find flock free getent grep groups gunzip gzip head help history hostname id jobs kill killall less ln ls man mkdir more mv nice nl nohup pgrep pkill printenv printf ps pwd renice readlink rev rm rmdir sed seq sh sleep sort source stat sudo tac tail tar tee test time top touch tr tree true type umask unalias uname uniq unset unxz unzip uptime wait wc which whoami xargs yes xz xzcat zcat zip'.split(' ');
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
    const t = n.type === 'd' ? 'd' : n.type === 'l' ? 'l' : n.type === 'c' ? 'c' : n.type === 'b' ? 'b' : n.type === 'p' ? 'p' : n.type === 's' ? 's' : '-';
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
      this.mkdirs('/usr/sbin'); SBIN.forEach(c => this.mk('/usr/sbin/' + c, 'f', 0o755, 'root', '#!practice ' + c + '\n'));
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
      this.sd();
    }
    now() { this.clock += 1000; return this.clock; }
    abs(p) { p = String(p); if (p === '~' || p.startsWith('~/')) p = HOME + p.slice(1); return norm(p.startsWith('/') ? p : this.cwd + '/' + p); }
    /* find a node. follow = true follows a symbolic link at the end of the path too */
    node(path, follow = true, depth = 0) {
      const parts = norm(path).split('/').filter(Boolean);
      if (parts[0] === 'proc' && this.procFs && !this.inProcFs) { this.inProcFs = true; try { this.procFs(); } finally { this.inProcFs = false; } }
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
      n.ino = this.inoNext = (this.inoNext || 1310714) + 7;
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
    size(n) { if (n.proc) return n.type === 'l' ? 64 : 0; if (n.big) return n.big; if (n.type === 'f' && n.data && n.data.charCodeAt(0) === 0 && this.unpack && this.unpack(n.data)) return this.unpack(n.data).size; return n.type === 'd' ? 4096 : n.type === 'l' ? n.target.length : n.type === 'c' ? 0 : enc(n.data); }
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
        const direct = this.viaPath; this.viaPath = false;
        if (!hit && !direct && (CMDS.includes(name) || SBIN.includes(name) || PKGCMDS.includes(name))) { this.eout(`${name}: command not found\n`); return 127; }
      }
      this.cmdNameReal = name; const f = C[name];
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
      if (/^#!practice /.test(n.data)) { this.viaPath = true; return this.call([n.data.slice(10).trim()].concat(args), input); }
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
    const nlink = n => this.links(n);
    const sz = n => String(hum ? human(this.size(n)) : this.size(n));
    let IW = 1; const ino = n => f.i ? pad(this.ino(n), IW) + ' ' : '';
    let W = [1, 1, 1, 1];
    const widths = rows => { W = [0, 0, 0, 0]; IW = Math.max(1, ...rows.map(([n]) => String(this.ino(n)).length)); rows.forEach(([n]) => { W = [Math.max(W[0], String(nlink(n)).length), Math.max(W[1], n.owner.length), Math.max(W[2], n.group.length), Math.max(W[3], sz(n).length)]; }); };
    const show = (n, name) => {
      if (!long) return ino(n) + name;
      const tgt = n.type === 'l' ? ' -> ' + n.target : '';
      return `${ino(n)}${modeStr(n)} ${pad(nlink(n), W[0])} ${pad(n.owner, W[1], true)} ${pad(n.group, W[2], true)} ${pad(sz(n), W[3])} ${when(n.mtime)} ${name}${tgt}`;
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
    if (files.length) { widths(files); if (!long) IW = 1; parts.push(files.map(([n, t]) => show(n, t)).join(long || f['1'] || this.notty ? '\n' : '  ')); }
    const walk = (n, t, head) => {
      if (!this.can(n, 'r')) { listing(n, t); return ''; }
      const rows = listing(n, t);
      let s = head ? `${t}:\n` : '';
      if (long) s += `total ${rows.reduce((sum, [m]) => sum + (m.proc ? 0 : m.type === 'd' ? 4 : this.size(m) ? Math.ceil(this.size(m) / 4096) * 4 : 0), 0)}\n`;
      widths(rows); if (!long) IW = 1;
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
    if (own && !this.pwRow(own)) { this.eout(`chown: invalid user: '${own}'\n`); return 1; }
    let code = 0;
    rest.forEach(t => {
      const n = this.node(this.abs(t));
      if (!n) { this.eout(`chown: cannot access '${t}': No such file or directory\n`); code = 1; return; }
      const mine = this.user === 'learner' ? ['learner', 'sudo'] : [this.user];
      const okGroupOnly = !own && grp && n.owner === this.user && mine.includes(grp);
      if (grp && !this.grRow(grp)) { this.eout(`${this.cmdName || 'chown'}: invalid group: '${grp}'\n`); code = 1; return; }
      if (this.user !== 'root' && !okGroupOnly) { this.eout(own ? `chown: changing ownership of '${t}': Operation not permitted\n` : `chgrp: changing group of '${t}': Operation not permitted\n`); code = 1; return; }
      const walk = m => { if (own) m.owner = own; if (grp !== undefined) m.group = grp || own; if (f.R && m.type === 'd') Object.values(m.kids).forEach(walk); };
      walk(n);
    });
    return code;
  };
  C.chgrp = function (a) { this.cmdName = 'chgrp'; try { return C.chown.call(this, [':' + a[0]].concat(a.slice(1))); } finally { this.cmdName = ''; } };
  C.whoami = function () { this.out(this.user + '\n'); };
  /* ---------- user accounts: /etc/passwd, /etc/group and /etc/shadow are the only source ---------- */
  World.prototype.dbRows = function (file) { const n = this.node(file); return n ? n.data.split('\n').filter(l => l && !l.startsWith('#')).map(l => l.split(':')) : []; };
  World.prototype.dbSave = function (file, rows) { this.node(file).data = rows.map(r => r.join(':')).join('\n') + '\n'; this.node(file).mtime = this.now(); };
  World.prototype.pwRow = function (u) { return this.dbRows('/etc/passwd').find(r => r[0] === u); };
  World.prototype.grRow = function (g) { return this.dbRows('/etc/group').find(r => r[0] === g); };
  World.prototype.userGroups = function (u) {
    const pw = this.pwRow(u), gr = this.dbRows('/etc/group'), prim = gr.find(r => r[2] === pw[3]);
    return [prim || [u, 'x', pw[3]]].concat(gr.filter(r => r !== prim && (r[3] || '').split(',').includes(u)));
  };
  C.id = function (a) {
    const u = a.filter(x => !x.startsWith('-'))[0] || this.user, pw = this.pwRow(u);
    if (!pw) { this.eout(`id: '${u}': no such user\n`); return 1; }
    const gs = this.userGroups(u);
    if (a.includes('-u')) { this.out((a.includes('-n') ? u : pw[2]) + '\n'); return 0; }
    if (a.includes('-G')) { this.out(gs.map(g => a.includes('-n') ? g[0] : g[2]).join(' ') + '\n'); return 0; }
    this.out(`uid=${pw[2]}(${u}) gid=${pw[3]}(${gs[0][0]}) groups=${gs.map(g => `${g[2]}(${g[0]})`).join(',')}\n`);
    return 0;
  };
  C.groups = function (a) {
    if (!a.length) { this.out(this.userGroups(this.user).map(g => g[0]).join(' ') + '\n'); return 0; }
    let code = 0;
    a.forEach(u => { if (!this.pwRow(u)) { this.eout(`groups: '${u}': no such user\n`); code = 1; } else this.out(`${u} : ${this.userGroups(u).map(g => g[0]).join(' ')}\n`); });
    return code;
  };
  World.prototype.needRoot = function (cmd, file) {
    if (this.user === 'root') return false;
    this.eout(`${cmd}: Permission denied.\n${cmd}: cannot lock ${file}; try again later.\n`); return true;
  };
  const nextId = (rows, col) => { const used = rows.map(r => +r[col]).filter(n => n >= 1000 && n < 60000); return used.length ? Math.max(...used) + 1 : 1000; };
  World.prototype.today = function () { return Math.floor(this.clock / 864e5); };
  C.useradd = function (a) {
    const o = { G: '' }; let name = null;
    for (let i = 0; i < a.length; i++) {
      const x = a[i];
      if (x === '-m' || x === '--create-home') o.m = true;
      else if (x === '-M') o.m = false;
      else if (x === '-r' || x === '--system') o.r = true;
      else if (/^-[scudgGe]$/.test(x)) o[x[1]] = a[++i];
      else if (x.startsWith('-')) { this.eout(`useradd: invalid option -- '${x.replace(/^-+/, '')}'\n`); return 2; }
      else name = x;
    }
    if (!name) { this.eout('Usage: useradd [options] LOGIN\n'); return 2; }
    if (this.needRoot('useradd', '/etc/passwd')) return 1;
    if (!/^[a-z_][a-z0-9_-]*\$?$/.test(name)) { this.eout(`useradd: invalid user name '${name}': use --badname to ignore\n`); return 3; }
    const pw = this.dbRows('/etc/passwd'), gr = this.dbRows('/etc/group');
    if (pw.some(r => r[0] === name)) { this.eout(`useradd: user '${name}' already exists\n`); return 9; }
    const extra = o.G ? o.G.split(',') : [];
    for (const g of extra.concat(o.g ? [o.g] : [])) if (!gr.some(r => r[0] === g || r[2] === g)) { this.eout(`useradd: group '${g}' does not exist\n`); return 6; }
    const uid = o.u !== undefined ? o.u : String(o.r ? 999 - pw.filter(r => +r[2] >= 100 && +r[2] < 1000 && r[0] !== 'www-data').length : nextId(pw, 2));
    if (pw.some(r => r[2] === uid)) { this.eout(`useradd: UID ${uid} is not unique\n`); return 4; }
    let gid;
    if (o.g) gid = gr.find(r => r[0] === o.g || r[2] === o.g)[2];
    else {
      if (gr.some(r => r[0] === name)) { this.eout(`useradd: group ${name} exists - if you want to add this user to that group, use -g.\n`); return 9; }
      gid = gr.some(r => r[2] === uid) ? String(nextId(gr, 2)) : uid; gr.push([name, 'x', gid, '']);
    }
    extra.forEach(g => { const r = gr.find(x => x[0] === g || x[2] === g); r[3] = (r[3] ? r[3].split(',') : []).concat(name).join(','); });
    const home = o.d || '/home/' + name, shell = o.s || '/bin/sh';
    pw.push([name, 'x', uid, gid, o.c || '', home, shell]);
    this.dbSave('/etc/passwd', pw); this.dbSave('/etc/group', gr);
    const sh = this.dbRows('/etc/shadow'); sh.push([name, '!', String(this.today()), '0', '99999', '7', '', '', '']); this.dbSave('/etc/shadow', sh);
    if (o.m && !this.node(home)) { this.mkdirs(dirName(home)); const h = this.mk(home, 'd', 0o750, name, ''); h.group = gr.find(r => r[2] === gid)[0]; h.mtime = this.now();
      ['.bashrc', '.profile', '.bash_logout'].forEach(f => { const src = this.node('/etc/skel/' + f); if (src) { const n = this.mk(home + '/' + f, 'f', 0o644, name, src.data); n.group = h.group; } }); }
    return 0;
  };
  C.groupadd = function (a) {
    const name = a.filter(x => !x.startsWith('-'))[0];
    if (!name) { this.eout('Usage: groupadd [options] GROUP\n'); return 2; }
    if (this.needRoot('groupadd', '/etc/group')) return 10;
    const gr = this.dbRows('/etc/group');
    if (gr.some(r => r[0] === name)) { this.eout(`groupadd: group '${name}' already exists\n`); return 9; }
    gr.push([name, 'x', String(a.includes('-r') ? 999 - gr.filter(r => +r[2] >= 100 && +r[2] < 1000).length : nextId(gr, 2)), '']); this.dbSave('/etc/group', gr); return 0;
  };
  C.groupdel = function (a) {
    const name = a[0]; if (this.needRoot('groupdel', '/etc/group')) return 10;
    const gr = this.dbRows('/etc/group'), k = gr.findIndex(r => r[0] === name);
    if (k < 0) { this.eout(`groupdel: group '${name}' does not exist\n`); return 6; }
    const prim = this.dbRows('/etc/passwd').find(r => r[3] === gr[k][2]);
    if (prim) { this.eout(`groupdel: cannot remove the primary group of user '${prim[0]}'\n`); return 8; }
    gr.splice(k, 1); this.dbSave('/etc/group', gr); return 0;
  };
  C.usermod = function (a) {
    const name = a[a.length - 1], o = {};
    for (let i = 0; i < a.length - 1; i++) { const x = a[i]; if (x === '-a' || x === '--append') o.a = true; else if (x === '-aG') { o.a = true; o.G = a[++i]; } else if (x === '-L' || x === '-U') o[x[1]] = true; else if (/^-[GsclgdM]$/.test(x)) o[x[1]] = a[++i]; }
    if (!name || name.startsWith('-')) { this.eout('Usage: usermod [options] LOGIN\n'); return 2; }
    if (this.needRoot('usermod', '/etc/passwd')) return 1;
    const pw = this.dbRows('/etc/passwd'), gr = this.dbRows('/etc/group'), row = pw.find(r => r[0] === name);
    if (!row) { this.eout(`usermod: user '${name}' does not exist\n`); return 6; }
    if (o.G !== undefined) {
      const want = o.G ? o.G.split(',') : [];
      for (const g of want) if (!gr.some(r => r[0] === g)) { this.eout(`usermod: group '${g}' does not exist\n`); return 6; }
      gr.forEach(r => { let m = r[3] ? r[3].split(',') : []; if (!o.a) m = m.filter(x => x !== name); if (want.includes(r[0]) && !m.includes(name)) m.push(name); r[3] = m.join(','); });
    }
    if (o.s) row[6] = o.s; if (o.c !== undefined) row[4] = o.c; if (o.d) row[5] = o.d;
    if (o.l) { if (pw.some(r => r[0] === o.l)) { this.eout(`usermod: user '${o.l}' already exists\n`); return 9; } row[0] = o.l; gr.forEach(r => { r[3] = (r[3] || '').split(',').map(x => x === name ? o.l : x).join(','); }); }
    if (o.g) { const g = gr.find(r => r[0] === o.g || r[2] === o.g); if (!g) { this.eout(`usermod: group '${o.g}' does not exist\n`); return 6; } row[3] = g[2]; }
    const sh = this.dbRows('/etc/shadow'), srow = sh.find(r => r[0] === name);
    if (srow && o.L && !srow[1].startsWith('!')) srow[1] = '!' + srow[1];
    if (srow && o.U && srow[1].startsWith('!')) { if (srow[1] === '!') { this.eout("usermod: unlocking the user's password would result in a passwordless account.\nYou should set a password with usermod -p to unlock this user's password.\n"); return 0; } srow[1] = srow[1].slice(1); }
    if (srow && o.l) srow[0] = o.l;
    this.dbSave('/etc/passwd', pw); this.dbSave('/etc/group', gr); if (srow) this.dbSave('/etc/shadow', sh);
    return 0;
  };
  C.userdel = function (a) {
    const name = a.filter(x => !x.startsWith('-'))[0], rmHome = a.includes('-r');
    if (!name) { this.eout('Usage: userdel [options] LOGIN\n'); return 2; }
    if (this.needRoot('userdel', '/etc/passwd')) return 1;
    const pw = this.dbRows('/etc/passwd'), row = pw.find(r => r[0] === name);
    if (!row) { this.eout(`userdel: user '${name}' does not exist\n`); return 6; }
    if (this.procs && this.procs.some(p => p.user === name)) { this.eout(`userdel: user ${name} is currently used by process ${this.procs.find(p => p.user === name).pid}\n`); return 8; }
    const gr = this.dbRows('/etc/group').filter(r => !(r[0] === name && r[2] === row[3] && !r[3]));
    gr.forEach(r => { r[3] = (r[3] || '').split(',').filter(x => x && x !== name).join(','); });
    this.dbSave('/etc/passwd', pw.filter(r => r !== row)); this.dbSave('/etc/group', gr); this.dbSave('/etc/shadow', this.dbRows('/etc/shadow').filter(r => r[0] !== name));
    if (rmHome) { this.eout(`userdel: ${name} mail spool (/var/mail/${name}) not found\n`); if (this.node(row[5])) this.removeNode(row[5]); }
    return 0;
  };
  const shadowDate = d => new Date(+d * 864e5).toISOString().slice(0, 10);
  C.passwd = function (a) {
    const flag = a.find(x => /^-[SlueS]$/.test(x) || x === '--status'), name = a.filter(x => !x.startsWith('-'))[0] || this.user;
    if (name !== this.user && this.user !== 'root') { this.eout(`passwd: You may not view or modify password information for ${name}.\n`); return 1; }
    const sh = this.dbRows('/etc/shadow'), r = sh.find(x => x[0] === name);
    if (!this.pwRow(name)) { this.eout(`passwd: user '${name}' does not exist\n`); return 1; }
    if (flag === '-S' || flag === '--status') { const st = !r || r[1] === '' ? 'NP' : r[1].startsWith('!') || r[1].startsWith('*') ? 'L' : 'P'; this.out(`${name} ${st} ${r ? shadowDate(r[2]) : '1970-01-01'} ${r ? r[3] : 0} ${r ? r[4] : 99999} ${r ? r[5] : 7} -1\n`); return 0; }
    if (this.user !== 'root' && flag) { this.eout('passwd: Permission denied.\n'); return 1; }
    if (flag === '-l') { if (r && !r[1].startsWith('!')) r[1] = '!' + r[1]; this.dbSave('/etc/shadow', sh); this.out('passwd: password changed.\n'); return 0; }
    if (flag === '-u') { if (r && r[1].startsWith('!') && r[1].length > 1) r[1] = r[1].slice(1); this.dbSave('/etc/shadow', sh); this.out('passwd: password changed.\n'); return 0; }
    if (flag === '-e') { if (r) r[2] = '0'; this.dbSave('/etc/shadow', sh); this.out('passwd: password changed.\n'); return 0; }
    this.eout('passwd asks for the new password twice without showing it, which the practice shell cannot do. Try: echo "' + name + ':NewPass.42" | sudo chpasswd\n'); return 1;
  };
  C.chpasswd = function (a, input) {
    if (this.user !== 'root') { this.eout('chpasswd: Permission denied.\nchpasswd: cannot lock /etc/passwd; try again later.\n'); return 1; }
    const sh = this.dbRows('/etc/shadow'); let code = 0;
    (input || '').split('\n').filter(Boolean).forEach((l, i) => {
      const [u, pass] = [l.slice(0, l.indexOf(':')), l.slice(l.indexOf(':') + 1)];
      if (l.indexOf(':') < 0 || !this.pwRow(u)) { this.eout(`chpasswd: line ${i + 1}: user '${u}' does not exist\n`); code = 1; return; }
      let r = sh.find(x => x[0] === u); if (!r) { r = [u, '', '', '0', '99999', '7', '', '', '']; sh.push(r); }
      let h = 0; for (const ch of pass) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
      r[1] = '$y$j9T$practice$' + h.toString(36); r[2] = String(this.today());
    });
    this.dbSave('/etc/shadow', sh); return code;
  };
  C.chage = function (a) {
    const name = a.filter(x => !x.startsWith('-'))[0];
    if (!a.includes('-l')) { if (this.user !== 'root') { this.eout('chage: Permission denied.\n'); return 1; } }
    const r = this.dbRows('/etc/shadow').find(x => x[0] === name);
    if (!this.pwRow(name || '')) { this.eout(`chage: user '${name}' does not exist in /etc/passwd\n`); return 1; }
    if (this.user !== 'root' && name !== this.user) { this.eout('chage: Permission denied.\n'); return 1; }
    const i = a.indexOf('-M'); if (i >= 0) { const sh = this.dbRows('/etc/shadow'); sh.find(x => x[0] === name)[4] = a[i + 1]; this.dbSave('/etc/shadow', sh); return 0; }
    const fmt = d => { const t = new Date(+d * 864e5); return `${MON3[t.getUTCMonth()]} ${String(t.getUTCDate()).padStart(2, '0')}, ${t.getUTCFullYear()}`; };
    const max = r ? r[4] : '99999', last = r ? r[2] : '0';
    this.out(`Last password change\t\t\t\t\t: ${last === '0' ? 'password must be changed' : fmt(last)}\nPassword expires\t\t\t\t\t: ${max === '99999' || max === '' ? 'never' : fmt(+last + +max)}\nPassword inactive\t\t\t\t\t: never\nAccount expires\t\t\t\t\t\t: never\nMinimum number of days between password change\t\t: ${r ? r[3] : 0}\nMaximum number of days between password change\t\t: ${max}\nNumber of days of warning before password expires\t: ${r ? r[5] : 7}\n`);
    return 0;
  };
  C.getent = function (a) {
    const db = { passwd: '/etc/passwd', group: '/etc/group', shadow: '/etc/shadow', hosts: '/etc/hosts' }[a[0]];
    if (!db) { this.eout(a[0] ? `Unknown database: ${a[0]}\nTry \`getent --help' or \`getent --usage' for more information.\n` : 'getent: wrong number of arguments\n'); return a[0] ? 1 : 1; }
    if (a[0] === 'shadow' && this.user !== 'root') return 2;
    const lines = this.node(db).data.split('\n').filter(l => l && !l.startsWith('#'));
    if (a.length === 1) { this.out(lines.join('\n') + '\n'); return 0; }
    let code = 0;
    a.slice(1).forEach(k => {
      const hit = a[0] === 'hosts' ? lines.find(l => l.split(/\s+/).slice(1).includes(k) || l.split(/\s+/)[0] === k) : lines.find(l => l.split(':')[0] === k || (a[0] !== 'shadow' && l.split(':')[2] === k));
      if (hit) this.out((a[0] === 'hosts' ? hit.split(/\s+/)[0].padEnd(15) + ' ' + hit.split(/\s+/).slice(1).join(' ') : hit) + '\n'); else code = 2;
    });
    return code;
  };
  C.hostname = function (a) { if (a && (a[0] === '-I' || a[0] === '--all-ip-addresses')) { this.out(this.net().ifs.filter(i => i.up && i.name !== 'lo').flatMap(i => i.addrs.map(x => x.split('/')[0])).join(' ') + ' \n'); return 0; } this.out(HOST + '\n'); };
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
    const swk = this.disks().swaps.reduce((t, x) => t + x.size / 1024 - 4, 0), gi = k => k ? (Math.round(k / 1048576 * 10) / 10).toFixed(1) + 'Gi' : '0B';
    this.out(f.h ? '               total        used        free      shared  buff/cache   available\nMem:           7.7Gi       2.1Gi       3.0Gi       120Mi       2.6Gi       5.3Gi\nSwap:   ' + gi(swk).padStart(12) + '          0B ' + gi(swk).padStart(11) + '\n'
      : '               total        used        free      shared  buff/cache   available\nMem:         8048304     2201124     3142212      122880     2704968     5563880\nSwap:   ' + String(swk).padStart(12) + '           0 ' + String(swk).padStart(11) + '\n');
  };
  C.df = function (a) {
    const [f, rest] = opts(a);
    let rows = this.mountTable();
    if (rest.length) rows = rest.map(x => { const p = this.abs(x); return rows.filter(r => p === r.dir || p.startsWith(r.dir === '/' ? '/' : r.dir + '/')).sort((m, n) => n.dir.length - m.dir.length)[0]; }).filter(Boolean);
    const hs = k => { const b = k * 1024; if (b === 0) return '0'; const u = ['K', 'M', 'G', 'T']; let x = k, i = 0; while (x >= 1024 && i < 3) { x /= 1024; i++; } return (x < 10 ? Math.ceil(x * 10) / 10 : Math.ceil(x)).toString().replace(/^(\d)$/, '$1.0') + u[i]; };
    const T = f.T;
    const head = f.i ? ['Filesystem', 'Inodes', 'IUsed', 'IFree', 'IUse%', 'Mounted on'] : f.h ? ['Filesystem', 'Size', 'Used', 'Avail', 'Use%', 'Mounted on'] : ['Filesystem', '1K-blocks', 'Used', 'Available', 'Use%', 'Mounted on'];
    if (T) head.splice(1, 0, 'Type');
    const body = rows.map(r => { const v = f.i ? [r.inodes, r.iused, r.inodes - r.iused] : [r.blocks, r.used, r.avail]; const pct = f.i ? (r.inodes ? Math.ceil(r.iused * 100 / r.inodes) + '%' : '-') : (r.used ? Math.ceil(r.used * 100 / (r.used + r.avail)) + '%' : '0%'); const cells = [r.src].concat(T ? [r.type] : [], f.h && !f.i ? v.map(hs) : v.map(String), [pct, r.dir]); return cells; });
    const all = [head].concat(body), w = head.map((_, i) => Math.max(...all.map(c => c[i].length)));
    w[0] = Math.max(w[0], 14);
    this.out(all.map(c => c.map((x, i) => i === 0 ? x.padEnd(w[0]) : i === c.length - 1 ? x : (i === 1 && T ? x.padEnd(w[1]) : x.padStart(w[i]))).join(' ')).join('\n') + '\n');
    return 0;
  };
  /* ---------- block devices, partitions, file systems and mounts ---------- */
  const GiB = 1024 ** 3, MiB = 1024 ** 2;
  World.prototype.disks = function () {
    if (this.diskState) return this.diskState;
    const root = { type: 'ext4', uuid: 'b6e1c2a4-77aa-4e0f-9d3b-2f1c8a5e0d71', label: '', blocks: 41152736, used: 15204920, avail: 23834288, inodes: 2621440, iused: 412530, keep: true };
    const usbRoot = { type: 'd', name: '/', mode: 0o755, owner: 'root', group: 'root', mtime: T0 - 864e5 * 9, kids: {} };
    const usb = { type: 'vfat', uuid: '4A1B-2C3D', label: 'USBSTICK', blocks: 31254512, used: 2160, avail: 31252352, inodes: 0, iused: 0, tree: usbRoot };
    const st = this.diskState = {
      devs: [
        { name: 'sda', mm: '8:0', rm: 0, size: 40 * GiB, model: 'ATA QEMU HARDDISK (scsi)', label: 'gpt', parts: [{ name: 'sda1', mm: '8:1', size: 40 * GiB - 2 * MiB, start: MiB, pname: '', fs: root }] },
        { name: 'sdb', mm: '8:16', rm: 1, size: 62529536 * 512, model: 'SanDisk Cruzer Blade (scsi)', label: 'msdos', parts: [{ name: 'sdb1', mm: '8:17', size: 62529536 * 512 - MiB, start: MiB, pname: '', fs: usb }] },
        { name: 'sdc', mm: '8:32', rm: 0, size: 20 * GiB, model: 'ATA QEMU HARDDISK (scsi)', label: null, parts: [] },
        { name: 'sdd', mm: '8:48', rm: 0, size: 10 * GiB, model: 'ATA QEMU HARDDISK (scsi)', label: null, parts: [] }],
      mounts: [{ dev: 'sda1', dir: '/', opts: 'rw,relatime,errors=remount-ro' }],
      swaps: [{ name: '/swap.img', type: 'file', size: 2 * GiB, prio: -2 }], lvm: { pvs: {}, vgs: {}, lvs: [] }
    };
    if (!this.node('/swap.img')) { const sw = this.mk('/swap.img', 'f', 0o600, 'root', ''); sw.big = 2 * GiB; sw.swap = 'a3f6c1d2-5b7e-4c89-9d0a-1e2f3b4c5d6e'; }
    const put = (tree, path, data) => { let n = tree; const bits = path.split('/'); bits.slice(0, -1).forEach(b => { n.kids[b] = n.kids[b] || { type: 'd', name: b, mode: 0o755, owner: 'root', group: 'root', mtime: T0 - 864e5 * 9, kids: {} }; n = n.kids[b]; }); n.kids[bits[bits.length - 1]] = { type: 'f', name: bits[bits.length - 1], mode: 0o755, owner: 'root', group: 'root', mtime: T0 - 864e5 * 9, data }; };
    put(usbRoot, 'notes.txt', 'Things to back up: photos, the thesis, the music folder\n');
    put(usbRoot, 'photos/trip-01.jpg', 'JPEGDATA'); put(usbRoot, 'photos/trip-02.jpg', 'JPEGDATA');
    st.devs.forEach(d => { this.mk('/dev/' + d.name, 'b', 0o660, 'root', '').group = 'disk'; d.parts.forEach(p => { this.mk('/dev/' + p.name, 'b', 0o660, 'root', '').group = 'disk'; }); });
    return st;
  };
  World.prototype.partOf = function (dev) {
    const st = this.disks(); let d = String(dev || '');
    let m;
    if ((m = /^UUID=(.+)$/.exec(d))) { for (const x of st.devs.concat([{ parts: st.lvm.lvs }])) for (const p of x.parts) if (p.fs && p.fs.uuid === m[1].replace(/"/g, '')) return p; return null; }
    if ((m = /^LABEL=(.+)$/.exec(d))) { for (const x of st.devs.concat([{ parts: st.lvm.lvs }])) for (const p of x.parts) if (p.fs && p.fs.label === m[1].replace(/"/g, '')) return p; return null; }
    d = d.replace(/^\/dev\//, '');
    for (const lv of st.lvm.lvs) if (d === lv.vg + '/' + lv.lv || d === 'mapper/' + lv.vg + '-' + lv.lv || d === lv.name) return lv;
    for (const x of st.devs) { if (x.name === d) return x; for (const p of x.parts) if (p.name === d) return p; }
    return null;
  };
  World.prototype.mountTable = function () {
    const st = this.disks();
    const rows = st.mounts.map(m => { const p = this.partOf(m.dev), fs = p.fs; return { src: '/dev/' + m.dev, dir: m.dir, type: fs.type, opts: m.opts, blocks: fs.blocks, used: fs.used, avail: fs.avail, inodes: fs.inodes, iused: fs.iused }; });
    rows.splice(1, 0, { src: 'tmpfs', dir: '/dev/shm', type: 'tmpfs', opts: 'rw,nosuid,nodev', blocks: 4024152, used: 0, avail: 4024152, inodes: 1006038, iused: 1 });
    return rows;
  };
  const humanBin = b => { const u = ['B', 'K', 'M', 'G', 'T']; let x = b, i = 0; while (x >= 1024 && i < 4) { x /= 1024; i++; } return (Math.round(x * 10) / 10).toString().replace(/\.0$/, '') + u[i]; };
  const newUuid = (w, seed) => { let h = 2166136261; for (const ch of seed + w.clock) h = Math.imul(h ^ ch.charCodeAt(0), 16777619) >>> 0; const hex = n => { let s2 = ''; for (let i = 0; i < n; i++) { h = Math.imul(h ^ i, 16777619) >>> 0; s2 += (h % 16).toString(16); } return s2; }; return `${hex(8)}-${hex(4)}-4${hex(3)}-a${hex(3)}-${hex(12)}`; };

  /* ---------- LVM: physical volumes, volume groups and logical volumes (4 MiB extents) ---------- */
  const lvmSize = b => { const u = b >= GiB ? ['g', GiB] : ['m', MiB], v = b / u[1], r = Math.round(v * 100) / 100; return (r > v + 1e-9 ? '<' : '') + r.toFixed(2) + u[0]; };
  const lvmParse = (x, unit) => { const m = /^\+?([\d.]+)([kmgtKMGT]?)$/.exec(x || ''); if (!m) return NaN; return +m[1] * ({ k: 1024, m: MiB, g: GiB, t: GiB * 1024 }[(m[2] || unit || 'm').toLowerCase()]); };
  World.prototype.lvmTable = function (head, rows, right) {
    const all = [head].concat(rows), w = head.map((_, i) => Math.max(...all.map(r => String(r[i]).length)));
    return all.map((r, k) => '  ' + r.map((x, i) => k && right.includes(i) ? String(x).padStart(w[i]) : String(x).padEnd(w[i])).join(' ')).join('\n') + '\n';
  };
  World.prototype.pvFree = function (n) { const st = this.disks(); return st.lvm.pvs[n].pe - st.lvm.lvs.reduce((t, l) => t + l.segs.filter(g => g.pv === n).reduce((u, g) => u + g.n, 0), 0); };
  World.prototype.lvAlloc = function (lv, n) { const st = this.disks(); for (const pv of st.lvm.vgs[lv.vg].pvs) { if (!n) break; const k = Math.min(n, this.pvFree(pv)); if (k > 0) { const last = lv.segs[lv.segs.length - 1]; if (last && last.pv === pv) last.n += k; else lv.segs.push({ pv, n: k }); n -= k; } } lv.pvs = [...new Set(lv.segs.map(g => g.pv))]; };
  World.prototype.vgFree = function (vg) { const st = this.disks(), V = st.lvm.vgs[vg]; return V.pvs.reduce((t, p) => t + st.lvm.pvs[p].pe, 0) - st.lvm.lvs.filter(l => l.vg === vg).reduce((t, l) => t + l.le, 0); };
  const lvmRoot = (w, name) => { if (w.user !== 'root') { w.eout('  WARNING: Running as a non-root user. Functionality may be unavailable.\n  /run/lock/lvm/P_global:aux: open failed: Permission denied\n'); return false; } return true; };
  C.pvcreate = function (a) {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(), devs = a.filter(x => !x.startsWith('-')), yes = a.includes('-y') || a.includes('-ff');
    if (!devs.length) { this.eout('  No devices specified.\n'); return 3; }
    for (const d of devs) {
      const x = this.partOf(d), n = d.replace(/^\/dev\//, '');
      if (!x || x.lv) { this.eout(`  No device found for ${d}.\n`); return 5; }
      if (st.lvm.pvs[n]) { this.eout(`  Can't initialize physical volume "${d}" of volume group "${st.lvm.pvs[n].vg}" without -ff\n`); return 5; }
      if (x.parts && x.label) { this.eout(`  Cannot use ${d}: device is partitioned\n`); return 5; }
      if (st.mounts.some(m => m.dev === x.name)) { this.eout(`  Can't open ${d} exclusively.  Mounted filesystem?\n`); return 5; }
      if (x.fs && !yes) { this.eout(`WARNING: ${x.fs.type} signature detected on ${d} at offset ${{ ext4: 1080, xfs: 0, vfat: 82, swap: 4086 }[x.fs.type] || 0}. Wipe it? [y/n]: [n]\n  Aborted wiping of ${x.fs.type}.\n  1 existing signature left on the device.\n`); return 5; }
      if (x.fs) { this.out(`WARNING: ${x.fs.type} signature detected on ${d} at offset ${{ ext4: 1080, xfs: 0, vfat: 82, swap: 4086 }[x.fs.type] || 0}. Wipe it? [y/n]: [y]\n  Wiping ${x.fs.type} signature on ${d}.\n`); x.fs = null; }
      const pu = newUuid(this, 'pv' + n).replace(/-/g, '').replace(/[0-9a-f]/g, (c, i) => 'aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789'[(parseInt(c, 16) * 7 + i) % 36]); st.lvm.pvs[n] = { uuid: [pu.slice(0, 6), pu.slice(6, 10), pu.slice(10, 14), pu.slice(14, 18), pu.slice(18, 22), pu.slice(22, 26), pu.slice(26, 32)].join('-'), dev: '/dev/' + n, vg: '', pe: Math.floor((x.size - MiB) / (4 * MiB)), size: x.size };
      this.out(`  Physical volume "${d}" successfully created.\n`);
    }
    return 0;
  };
  C.pvremove = function (a) {
    if (!lvmRoot(this)) return 5;
    const st = this.disks();
    for (const d of a.filter(x => !x.startsWith('-'))) { const n = d.replace(/^\/dev\//, ''), P = st.lvm.pvs[n]; if (!P) { this.eout(`  No PV found on device ${d}.\n`); return 5; } if (P.vg) { this.eout(`  PV ${d} is used by VG ${P.vg} so please use vgreduce first.\n  (If you are certain you need pvremove, then confirm by using --force twice.)\n`); return 5; } delete st.lvm.pvs[n]; this.out(`  Labels on physical volume "${d}" successfully wiped.\n`); }
    return 0;
  };
  C.vgcreate = function (a) {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(), [vg, ...devs] = a.filter(x => !x.startsWith('-'));
    if (!vg || !devs.length) { this.eout('  Please provide volume group name and physical volumes\n'); return 3; }
    if (st.lvm.vgs[vg]) { this.eout(`  A volume group called ${vg} already exists.\n`); return 5; }
    for (const d of devs) { const n = d.replace(/^\/dev\//, ''); if (!st.lvm.pvs[n]) { const r = C.pvcreate.call(this, [d]); if (r) return r; } if (st.lvm.pvs[n].vg) { this.eout(`  Physical volume '${d}' is already in volume group '${st.lvm.pvs[n].vg}'\n  Unable to add physical volume '${d}' to volume group '${st.lvm.pvs[n].vg}'\n`); return 5; } }
    st.lvm.vgs[vg] = { pvs: devs.map(d => d.replace(/^\/dev\//, '')) };
    st.lvm.vgs[vg].pvs.forEach(n => { st.lvm.pvs[n].vg = vg; });
    this.out(`  Volume group "${vg}" successfully created\n`);
    return 0;
  };
  C.vgextend = function (a) {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(), [vg, ...devs] = a.filter(x => !x.startsWith('-'));
    if (!st.lvm.vgs[vg]) { this.eout(`  Volume group "${vg}" not found\n  Cannot process volume group ${vg}\n`); return 5; }
    for (const d of devs) { const n = d.replace(/^\/dev\//, ''); if (!st.lvm.pvs[n]) { const r = C.pvcreate.call(this, [d]); if (r) return r; } st.lvm.pvs[n].vg = vg; st.lvm.vgs[vg].pvs.push(n); }
    this.out(`  Volume group "${vg}" successfully extended\n`);
    return 0;
  };
  C.vgremove = function (a) {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(), vg = a.filter(x => !x.startsWith('-'))[0];
    if (!st.lvm.vgs[vg]) { this.eout(`  Volume group "${vg}" not found\n  Cannot process volume group ${vg}\n`); return 5; }
    if (st.lvm.lvs.some(l => l.vg === vg)) { this.eout(`  Volume group "${vg}" still contains ${st.lvm.lvs.filter(l => l.vg === vg).length} logical volume(s). Remove them first with lvremove.\n`); return 5; }
    st.lvm.vgs[vg].pvs.forEach(n => { st.lvm.pvs[n].vg = ''; }); delete st.lvm.vgs[vg];
    this.out(`  Volume group "${vg}" successfully removed\n`);
    return 0;
  };
  C.lvcreate = function (a) {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(); let name = '', L = '', l = '', vg = '';
    for (let i = 0; i < a.length; i++) { if (a[i] === '-n' || a[i] === '--name') name = a[++i]; else if (a[i] === '-L' || a[i] === '--size') L = a[++i]; else if (a[i] === '-l' || a[i] === '--extents') l = a[++i]; else if (a[i] === '-y') ; else if (!a[i].startsWith('-')) vg = a[i]; }
    if (!st.lvm.vgs[vg]) { this.eout(`  Volume group "${vg}" not found\n  Cannot process volume group ${vg}\n`); return 5; }
    if (!name) name = 'lvol' + st.lvm.lvs.filter(x => x.vg === vg).length;
    if (st.lvm.lvs.some(x => x.vg === vg && x.lv === name)) { this.eout(`  Logical Volume "${name}" already exists in volume group "${vg}"\n`); return 5; }
    const free = this.vgFree(vg); let le;
    if (L) le = Math.ceil(lvmParse(L, 'm') / (4 * MiB)); else if (/^(\d+)%FREE$/.test(l)) le = Math.floor(free * +RegExp.$1 / 100); else if (/^(\d+)%VG$/.test(l)) le = Math.floor(st.lvm.vgs[vg].pvs.reduce((t, p) => t + st.lvm.pvs[p].pe, 0) * +RegExp.$1 / 100); else le = +l;
    if (!le || isNaN(le)) { this.eout('  Please specify either size or extents but not both.\n'); return 3; }
    if (le > free) { this.eout(`  Volume group "${vg}" has insufficient free space (${free} extents): ${le} required.\n`); return 5; }
    const lv = { lv: name, vg, name: 'mapper/' + vg + '-' + name, le, size: le * 4 * MiB, mm: '253:' + st.lvm.lvs.length, pvs: [], segs: [], fs: null, isLv: true };
    this.lvAlloc(lv, le); st.lvm.lvs.push(lv);
    this.mk(`/dev/${vg}`, 'd', 0o755, 'root', ''); this.mk(`/dev/${vg}/${name}`, 'b', 0o660, 'root', '').group = 'disk';
    this.out(`  Logical volume "${name}" created.\n`);
    return 0;
  };
  C.lvextend = C.lvresize = C.lvreduce = function (a) {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(); let L = '', l = '', target = '', fsToo = false;
    for (let i = 0; i < a.length; i++) { if (a[i] === '-L' || a[i] === '--size') L = a[++i]; else if (a[i] === '-l' || a[i] === '--extents') l = a[++i]; else if (a[i] === '-r' || a[i] === '--resizefs') fsToo = true; else if (!a[i].startsWith('-')) target = a[i]; }
    const lv = this.partOf(target);
    if (!lv || !lv.isLv) { this.eout(`  Failed to find logical volume "${String(target).replace(/^\/dev\//, '')}"\n`); return 5; }
    const free = this.vgFree(lv.vg), plus = /^\+/.test(L || l); let le;
    if (L) le = (plus ? lv.le : 0) + Math.ceil(lvmParse(L, 'm') / (4 * MiB)); else if (/^\+?(\d+)%FREE$/.test(l)) le = lv.le + Math.floor(free * +RegExp.$1 / 100); else le = (plus ? lv.le : 0) + +String(l).replace('+', '');
    const what = `${lv.vg}/${lv.lv}`, sz = e => `${lvmSize(e * 4 * MiB).replace(/^</, '').replace(/g$/, ' GiB').replace(/m$/, ' MiB')} (${e} extents)`;
    if (le < lv.le) { this.eout(`  The practice shell does not shrink volumes. Shrinking needs the file system made smaller first, and xfs cannot shrink at all.\n`); return 5; }
    if (le === lv.le) { this.eout(`  New size (${le} extents) matches existing size (${le} extents).\n`); return 5; }
    if (le - lv.le > free) { this.eout(`  Insufficient free space: ${le - lv.le} extents needed, but only ${free} available\n`); return 5; }
    const old = lv.le; this.lvAlloc(lv, le - old); lv.le = le; lv.size = le * 4 * MiB;
    this.out(`  Size of logical volume ${what} changed from ${sz(old)} to ${sz(le)}.\n  Logical volume ${what} successfully resized.\n`);
    if (fsToo && lv.fs && lv.fs.type === 'ext4') {
      const m = st.mounts.find(x => x.dev === lv.name), dev = '/dev/' + lv.name, nb = Math.floor(lv.size / 4096), desc = n => Math.ceil(Math.ceil(n / 32768) * 64 / 4096);
      this.out(`resize2fs 1.47.0 (5-Feb-2023)\n${m ? `Filesystem at ${dev} is mounted on ${m.dir}; on-line resizing required\n` : ''}old_desc_blocks = ${desc(Math.floor(old * 4 * MiB / 4096))}, new_desc_blocks = ${desc(nb)}\nThe filesystem on ${dev} is now ${nb} (4k) blocks long.\n\n`);
      const k = nb * 4; lv.fs.blocks = Math.round(k * 0.976); lv.fs.avail = Math.round(k * 0.925); lv.fs.inodes = Math.floor(nb / 4 / 8192) * 8192 || 8192;
    } else if (fsToo && lv.fs && lv.fs.type === 'xfs') { const k = lv.size / 1024; lv.fs.blocks = Math.round(k * 0.995); lv.fs.avail = Math.round(k * 0.9875); }
    return 0;
  };
  C.lvremove = function (a) {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(), lv = this.partOf(a.filter(x => !x.startsWith('-'))[0]);
    if (!lv || !lv.isLv) { this.eout('  Failed to find logical volume\n'); return 5; }
    if (st.mounts.some(m => m.dev === lv.name)) { this.eout(`  Logical volume ${lv.vg}/${lv.lv} contains a filesystem in use.\n`); return 5; }
    st.lvm.lvs.splice(st.lvm.lvs.indexOf(lv), 1); this.out(`  Logical volume "${lv.lv}" successfully removed.\n`);
    return 0;
  };
  C.pvs = function () {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(), rows = Object.keys(st.lvm.pvs).map(n => { const P = st.lvm.pvs[n], used = P.pe - this.pvFree(n); return [P.dev, P.vg, 'lvm2', P.vg ? 'a--' : '---', P.vg ? lvmSize(P.pe * 4 * MiB) : lvmSize(P.size), P.vg ? lvmSize((P.pe - used) * 4 * MiB).replace(/^0\.00[gm]$/, '0 ') : lvmSize(P.size)]; });
    if (rows.length) this.out(this.lvmTable(['PV', 'VG', 'Fmt', 'Attr', 'PSize', 'PFree'], rows, [4, 5]));
    return 0;
  };
  C.vgs = function () {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(), rows = Object.keys(st.lvm.vgs).map(vg => { const V = st.lvm.vgs[vg], tot = V.pvs.reduce((t, p) => t + st.lvm.pvs[p].pe, 0), fr = this.vgFree(vg); return [vg, V.pvs.length, st.lvm.lvs.filter(l => l.vg === vg).length, 0, 'wz--n-', lvmSize(tot * 4 * MiB), fr ? lvmSize(fr * 4 * MiB) : '0 ']; });
    if (rows.length) this.out(this.lvmTable(['VG', '#PV', '#LV', '#SN', 'Attr', 'VSize', 'VFree'], rows, [1, 2, 3, 5, 6]));
    else this.out('  No volume groups found\n');
    return 0;
  };
  C.lvs = function () {
    if (!lvmRoot(this)) return 5;
    const st = this.disks(), rows = st.lvm.lvs.map(l => [l.lv, l.vg, st.mounts.some(m => m.dev === l.name) || st.swaps.some(x => x.dev === l) ? '-wi-ao----' : '-wi-a-----', lvmSize(l.size)]);
    if (rows.length) this.out(this.lvmTable(['LV', 'VG', 'Attr', 'LSize'], rows, [3]).replace(/^(  LV[^\n]*LSize *)/, '$1 Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert'));
    return 0;
  };

  /* ---------- swap: fallocate, mkswap, swapon, swapoff ---------- */
  C.fallocate = function (a) {
    let len = '', t = '';
    for (let i = 0; i < a.length; i++) { if (a[i] === '-l' || a[i] === '--length') len = a[++i]; else if (!a[i].startsWith('-')) t = a[i]; }
    const m = /^([\d.]+)([KMGT]?)/i.exec(len || ''); const b = m ? +m[1] * ({ '': 1, k: 1024, m: MiB, g: GiB, t: GiB * 1024 }[m[2].toLowerCase()]) : NaN;
    if (!t || isNaN(b)) { this.eout('fallocate: no length argument specified\n'); return 1; }
    const p = this.abs(t), parent = this.node(dirName(p));
    if (!parent) { this.eout(`fallocate: cannot open ${t}: No such file or directory\n`); return 1; }
    let n = this.node(p);
    if (!n) { if (!this.can(parent, 'w')) { this.eout(`fallocate: cannot open ${t}: Permission denied\n`); return 1; } n = this.mk(p, 'f', 0o666 & ~this.umask, this.user, ''); n.mtime = this.now(); }
    n.big = Math.max(this.size(n), b);
    return 0;
  };
  C.mkswap = function (a) {
    const t = a.filter(x => !x.startsWith('-'))[0];
    if (!t) { this.eout('mkswap: no device specified\n'); return 1; }
    const x = this.partOf(t), n = x ? null : this.node(this.abs(t));
    if (!x && !n) { this.eout(`mkswap: cannot open ${t}: No such file or directory\n`); return 1; }
    if (this.user !== 'root') { this.eout(`mkswap: cannot open ${t}: Permission denied\n`); return 1; }
    const size = x ? x.size : this.size(n), uuid = newUuid(this, 'swap' + t);
    if (n && (n.mode & 0o077)) this.eout(`mkswap: ${t}: insecure permissions ${(n.mode & 0o777).toString(8).padStart(4, '0')}, fix with: chmod 0600 ${t}\n`);
    if (x && st0(this).swaps.some(s => s.dev === x)) { this.eout(`mkswap: ${t}: contains a swap area that is in use\n`); return 1; }
    this.out(`Setting up swapspace version 1, size = ${humanMiB(size - 4096)} (${size - 4096} bytes)\nno label, UUID=${uuid}\n`);
    if (x) x.fs = { type: 'swap', uuid, label: '', blocks: 0, used: 0, avail: 0, inodes: 0, iused: 0 }; else n.swap = uuid;
    return 0;
  };
  const st0 = w => w.disks();
  const humanMiB = b => { const m = b / MiB; return (Number.isInteger(m) ? m : m.toFixed(0)) + ' MiB'; };
  C.swapon = function (a) {
    const st = this.disks(), args = a.filter(x => !x.startsWith('-'));
    const show = () => { if (!st.swaps.length) return 0; this.out(['NAME TYPE SIZE USED PRIO'].concat(st.swaps.map(x => `${x.name} ${x.type} ${humanBin(x.size - 4096).replace(/(\.\d)?([KMGT])$/, (m0, d, u) => (d || '') + u)} 0B ${x.prio}`)).map(l => l.split(' ')).reduce((acc, r, i, A) => { const w = A[0].map((_, k) => Math.max(...A.map(q => q[k].length))); acc.push(r.map((c, k) => k === 0 || k === 1 ? c.padEnd(w[k]) : c.padStart(w[k])).join(' ')); return acc; }, []).join('\n') + '\n'); return 0; };
    if (!args.length && !a.includes('-a')) return show();
    if (this.user !== 'root') { this.eout(`swapon: ${args[0] || '/etc/fstab'}: Permission denied\n`); return 1; }
    const one = t => {
      if (st.swaps.some(x => x.name === t || (x.dev && this.partOf(t) === x.dev))) { this.eout(`swapon: ${t}: swapon failed: Device or resource busy\n`); return 255; }
      const x = this.partOf(t), n = x ? null : this.node(this.abs(t));
      if (!x && !n) { this.eout(`swapon: cannot open ${t}: No such file or directory\n`); return 255; }
      if (x ? !(x.fs && x.fs.type === 'swap') : !n.swap) { this.eout(`swapon: ${t}: read swap header failed\n`); return 255; }
      if (n && (n.mode & 0o077)) this.eout(`swapon: ${t}: insecure permissions ${(n.mode & 0o777).toString(8).padStart(4, '0')}, 0600 suggested.\n`);
      st.swaps.push(x ? { name: '/dev/' + (x.isLv ? 'dm-' + x.mm.split(':')[1] : x.name), type: 'partition', size: x.size, prio: -2 - st.swaps.length, dev: x } : { name: this.abs(t), type: 'file', size: this.size(n), prio: -2 - st.swaps.length });
      return 0;
    };
    if (a.includes('-a')) { const tab = (this.node('/etc/fstab').data || '').split('\n').map(l => l.trim().split(/\s+/)).filter(f => f[2] === 'swap' && !f[0].startsWith('#')); for (const f of tab) { const p = this.partOf(f[0]); const nm = p ? '/dev/' + p.name : f[0]; if (!st.swaps.some(x => x.name === nm || x.dev === p)) { const r = one(f[0]); if (r) return r; } } return 0; }
    for (const t of args) { const r = one(t); if (r) return r; }
    return 0;
  };
  C.swapoff = function (a) {
    const st = this.disks(), args = a.filter(x => !x.startsWith('-'));
    if (this.user !== 'root') { this.eout(`swapoff: ${args[0] || ''}: Operation not permitted\n`); return 1; }
    if (a.includes('-a')) { st.swaps.length = 0; return 0; }
    for (const t of args) { const p = this.partOf(t), i = st.swaps.findIndex(x => x.name === this.abs(t) || (p && x.dev === p)); if (i < 0) { this.eout(`swapoff: ${t}: swapoff failed: Invalid argument\n`); return 255; } st.swaps.splice(i, 1); }
    return 0;
  };

  /* ---------- networking: one interface on a home or office network, a router, a file server and two web hosts ---------- */
  const NGINX_PAGE = '<!DOCTYPE html>\n<html>\n<head>\n<title>Welcome to nginx!</title>\n<style>\nhtml { color-scheme: light dark; }\nbody { width: 35em; margin: 0 auto;\nfont-family: Tahoma, Verdana, Arial, sans-serif; }\n</style>\n</head>\n<body>\n<h1>Welcome to nginx!</h1>\n<p>If you see this page, the nginx web server is successfully installed and\nworking. Further configuration is required.</p>\n\n<p>For online documentation and support please refer to\n<a href="http://nginx.org/">nginx.org</a>.<br/>\nCommercial support is available at\n<a href="http://nginx.com/">nginx.com</a>.</p>\n\n<p><em>Thank you for using nginx.</em></p>\n</body>\n</html>\n';
  const SERVICES = { 22: 'ssh', 25: 'smtp', 53: 'domain', 80: 'http', 443: 'https', 3306: 'mysql', 5432: 'postgresql', 8080: 'http-alt' };
  const ip4 = x => x.split('.').reduce((t, o) => t * 256 + +o, 0);
  const inNet = (ip, cidr) => { const [n, b] = cidr.split('/'), m = b === '0' ? 0 : (~0 << (32 - +b)) >>> 0; return ((ip4(ip) & m) >>> 0) === ((ip4(n) & m) >>> 0); };
  const netOf = cidr => { const [n, b] = cidr.split('/'), m = (~0 << (32 - +b)) >>> 0, v = (ip4(n) & m) >>> 0; return [v >>> 24, (v >>> 16) & 255, (v >>> 8) & 255, v & 255].join('.') + '/' + b; };
  const bcastOf = cidr => { const [n, b] = cidr.split('/'), m = (~0 << (32 - +b)) >>> 0, v = ((ip4(n) & m) | ~m) >>> 0; return [v >>> 24, (v >>> 16) & 255, (v >>> 8) & 255, v & 255].join('.'); };
  World.prototype.net = function () {
    if (this.netState) return this.netState;
    const st = this.netState = {
      ifs: [{ name: 'lo', idx: 1, mac: '00:00:00:00:00:00', up: true, mtu: 65536, addrs: ['127.0.0.1/8'] },
            { name: 'enp0s3', idx: 2, mac: '52:54:00:12:34:56', up: true, mtu: 1500, addrs: ['192.168.1.50/24'] }],
      routes: [{ dst: 'default', via: '192.168.1.1', dev: 'enp0s3', proto: 'static' }, { dst: '192.168.1.0/24', dev: 'enp0s3', proto: 'kernel', src: '192.168.1.50' }],
      hosts: { '192.168.1.1': { mac: '52:54:00:aa:01:01', ms: 0.41, ttl: 64, ports: [53] }, '192.168.1.20': { mac: '52:54:00:aa:01:14', ms: 0.62, ttl: 64, ports: [22, 445] },
               '198.51.100.80': { ms: 11.8, ttl: 56, ports: [80, 443], hops: ['192.168.1.1', '203.0.113.1', '198.51.100.1'] }, '198.51.100.25': { ms: 12.3, ttl: 56, ports: [25], hops: ['192.168.1.1', '203.0.113.1', '198.51.100.1'] } },
      dns: { 'www.shop.lab': ['A', '198.51.100.80'], 'shop.lab': ['A', '198.51.100.80'], 'mail.shop.lab': ['A', '198.51.100.25'], 'files.shop.lab': ['A', '192.168.1.20'] },
      mx: { 'shop.lab': '10 mail.shop.lab.' }, neigh: {}
    };
    if (!this.node('/etc/resolv.conf')) this.mk('/etc/resolv.conf', 'f', 0o644, 'root', '# This is /run/systemd/resolve/stub-resolv.conf managed by man:systemd-resolved(8).\n# Do not edit.\n\nnameserver 127.0.0.53\noptions edns0 trust-ad\nsearch .\n');
    if (!this.node('/etc/netplan/01-netcfg.yaml')) { this.mkdirs('/etc/netplan'); this.mk('/etc/netplan/01-netcfg.yaml', 'f', 0o600, 'root', 'network:\n  version: 2\n  ethernets:\n    enp0s3:\n      addresses:\n        - 192.168.1.50/24\n      routes:\n        - to: default\n          via: 192.168.1.1\n      nameservers:\n        addresses: [192.168.1.1]\n'); }
    if (!this.node('/var/www/html/index.nginx-debian.html')) { this.mkdirs('/var/www/html'); this.mk('/var/www/html/index.nginx-debian.html', 'f', 0o644, 'root', NGINX_PAGE); }
    return st;
  };
  World.prototype.resolve = function (name) {
    if (/^\d+\.\d+\.\d+\.\d+$/.test(name)) return name;
    if (name === 'localhost') return '127.0.0.1';
    const h = (this.node('/etc/hosts').data || '').split('\n').map(l => l.replace(/#.*/, '').trim().split(/\s+/)).find(f => f.length > 1 && f.slice(1).includes(name));
    if (h) return h[0];
    const st = this.net(), d = st.dns[name.replace(/\.$/, '')];
    return d && this.routeTo('192.168.1.1') ? d[1] : null;
  };
  World.prototype.routeTo = function (ip) {
    const st = this.net();
    if (/^127\./.test(ip) || st.ifs.some(i => i.addrs.some(a => a.split('/')[0] === ip))) return { dev: 'lo', local: true, src: ip };
    const up = r => { const i = st.ifs.find(x => x.name === r.dev); return i && i.up; };
    const best = st.routes.filter(r => up(r) && (r.dst === 'default' || inNet(ip, r.dst))).sort((a, b) => (b.dst === 'default' ? 0 : +b.dst.split('/')[1]) - (a.dst === 'default' ? 0 : +a.dst.split('/')[1]))[0];
    if (!best) return null;
    const i = st.ifs.find(x => x.name === best.dev), src = (i.addrs[0] || '').split('/')[0];
    return { dev: best.dev, via: best.via, src };
  };
  World.prototype.reach = function (ip) {
    const r = this.routeTo(ip); if (!r) return null;
    if (r.local) return { local: true, ms: 0.04, ttl: 64, ports: this.listening().map(l => l.port) };
    const st = this.net(), gw = r.via, onLink = !gw;
    if (onLink) { const h = st.hosts[ip]; if (h && h.mac) st.neigh[ip] = h.mac; return h && h.mac ? h : { unreachable: true }; }
    if (!st.hosts[gw]) return { unreachable: true, gw };
    st.neigh[gw] = st.hosts[gw].mac;
    return st.hosts[ip] || { lost: true };
  };
  World.prototype.listening = function () {
    const u = this.sd ? this.sd().units : {}, L = [{ addr: '127.0.0.54', port: 53, prog: 'systemd-resolve', pid: 388, fd: 16, q: 0, udp: true }, { addr: '127.0.0.53%lo', port: 53, prog: 'systemd-resolve', pid: 388, fd: 14, q: 0, udp: true }, { addr: '127.0.0.54', port: 53, prog: 'systemd-resolve', pid: 388, fd: 17, q: 4096 }, { addr: '127.0.0.53%lo', port: 53, prog: 'systemd-resolve', pid: 388, fd: 15, q: 4096 }];
    if (u['ssh.service'] && u['ssh.service'].state === 'active') L.push({ addr: '0.0.0.0', port: 22, prog: 'sshd', pid: u['ssh.service'].mainPid, fd: 3, q: 4096 }, { addr: '[::]', port: 22, prog: 'sshd', pid: u['ssh.service'].mainPid, fd: 4, q: 4096 });
    if (u['nginx.service'] && u['nginx.service'].state === 'active') L.push({ addr: '0.0.0.0', port: 80, prog: 'nginx', pid: u['nginx.service'].mainPid, fd: 6, q: 511 }, { addr: '[::]', port: 80, prog: 'nginx', pid: u['nginx.service'].mainPid, fd: 7, q: 511 });
    return L;
  };
  C.ip = function (a0) {
    const st = this.net(); let a = a0.slice(); const br = a.includes('-br') || a.includes('-brief'), only4 = a.includes('-4');
    a = a.filter(x => !['-br', '-brief', '-4', '-c', '-color'].includes(x));
    const obj = a[0] || 'help', verb = a[1] || 'show', rest = a.slice(2);
    const need = () => { if (this.user !== 'root') { this.eout('RTNETLINK answers: Operation not permitted\n'); return true; } return false; };
    const dev = n => st.ifs.find(i => i.name === n);
    const devArg = () => { const k = rest.indexOf('dev'); return k >= 0 ? rest[k + 1] : rest.find(x => dev(x)); };
    const flags = i => i.name === 'lo' ? (i.up ? '<LOOPBACK,UP,LOWER_UP>' : '<LOOPBACK>') : (i.up ? '<BROADCAST,MULTICAST,UP,LOWER_UP>' : '<BROADCAST,MULTICAST>');
    const state = i => i.name === 'lo' ? (i.up ? 'UNKNOWN' : 'DOWN') : i.up ? 'UP' : 'DOWN';
    const v6 = i => i.name === 'lo' ? '::1/128' : 'fe80::5054:ff:fe12:3456/64';
    const linkLine = i => `${i.idx}: ${i.name}: ${flags(i)} mtu ${i.mtu} qdisc ${i.name === 'lo' ? 'noqueue' : 'fq_codel'} state ${state(i)} ${i.name === 'lo' ? '' : ''}mode DEFAULT group default qlen 1000\n    link/${i.name === 'lo' ? 'loopback' : 'ether'} ${i.mac} brd ${i.name === 'lo' ? '00:00:00:00:00:00' : 'ff:ff:ff:ff:ff:ff'}\n`;
    if (/^(a|ad|add|addr|address)$/.test(obj)) {
      if (verb === 'add' || verb === 'del' || verb === 'delete') {
        if (need()) return 2;
        const cidr = rest[0], i = dev(devArg());
        if (!i) { this.eout(`Cannot find device "${devArg() || ''}"\n`); return 1; }
        const c = /\//.test(cidr) ? cidr : cidr + '/32';
        if (verb === 'add') { if (i.addrs.includes(c)) { this.eout('RTNETLINK answers: File exists\n'); return 2; } i.addrs.push(c); if (!st.routes.some(r => r.dst === netOf(c) && r.dev === i.name)) st.routes.push({ dst: netOf(c), dev: i.name, proto: 'kernel', src: c.split('/')[0] }); }
        else { const k = i.addrs.indexOf(c); if (k < 0) { this.eout('RTNETLINK answers: Cannot assign requested address\n'); return 2; } i.addrs.splice(k, 1); if (!i.addrs.some(x => netOf(x) === netOf(c))) st.routes = st.routes.filter(r => !(r.dst === netOf(c) && r.dev === i.name)); }
        return 0;
      }
      const list = st.ifs.filter(i => !devArg() || i.name === devArg());
      if (devArg() && !list.length) { this.eout(`Device "${devArg()}" does not exist.\n`); return 1; }
      if (br) { this.out(list.map(i => `${i.name.padEnd(16)} ${state(i).padEnd(14)} ${i.addrs.concat(only4 || !i.up ? [] : [v6(i)]).join(' ')} `).join('\n') + '\n'); return 0; }
      this.out(list.map(i => linkLine(i).replace(' mode DEFAULT', '') + i.addrs.map(x => `    inet ${x} ${i.name === 'lo' ? 'scope host lo' : `brd ${bcastOf(x)} scope global ${i.name}`}\n       valid_lft forever preferred_lft forever\n`).join('') + (only4 || !i.up ? '' : `    inet6 ${v6(i)} scope ${i.name === 'lo' ? 'host noprefixroute' : 'link'} \n       valid_lft forever preferred_lft forever\n`)).join(''));
      return 0;
    }
    if (/^(l|li|link)$/.test(obj)) {
      if (verb === 'set') {
        if (need()) return 2;
        const i = dev(devArg()); if (!i) { this.eout(`Cannot find device "${devArg() || ''}"\n`); return 1; }
        if (rest.includes('down')) { i.up = false; st.routes = st.routes.filter(r => r.dev !== i.name); }
        if (rest.includes('up') && !i.up) { i.up = true; i.addrs.forEach(x => { if (!st.routes.some(r => r.dst === netOf(x) && r.dev === i.name) && i.name !== 'lo') st.routes.push({ dst: netOf(x), dev: i.name, proto: 'kernel', src: x.split('/')[0] }); }); }
        return 0;
      }
      const list = st.ifs.filter(i => !devArg() || i.name === devArg());
      if (br) { this.out(list.map(i => `${i.name.padEnd(16)} ${state(i).padEnd(14)} ${i.mac} ${flags(i)} `).join('\n') + '\n'); return 0; }
      this.out(list.map(linkLine).join('')); return 0;
    }
    if (/^(r|ro|route)$/.test(obj)) {
      if (verb === 'get') { const ip = rest[0], r = this.routeTo(ip || ''); if (!r) { this.eout('RTNETLINK answers: Network is unreachable\n'); return 2; } this.out(r.local ? `local ${ip} dev lo table local src ${r.src} uid ${this.uid()} \n    cache <local> \n` : `${ip} ${r.via ? `via ${r.via} ` : ''}dev ${r.dev} src ${r.src} uid ${this.uid()} \n    cache \n`); return 0; }
      if (verb === 'add' || verb === 'del' || verb === 'delete' || verb === 'replace') {
        if (need()) return 2;
        const dst = rest[0], k = rest.indexOf('via'), via = k >= 0 ? rest[k + 1] : undefined, d = devArg() || (via ? (this.routeTo(via) || {}).dev : undefined);
        if (verb === 'add' && st.routes.some(r => r.dst === dst)) { this.eout('RTNETLINK answers: File exists\n'); return 2; }
        if (verb === 'add' || verb === 'replace') { if (via && !st.routes.some(r => r.dst !== 'default' && inNet(via, r.dst))) { this.eout('Error: Nexthop has invalid gateway.\n'); return 2; } st.routes = st.routes.filter(r => r.dst !== dst); st.routes.unshift({ dst, via, dev: d || 'enp0s3', proto: 'boot' }); }
        else { const n = st.routes.length; st.routes = st.routes.filter(r => r.dst !== dst); if (st.routes.length === n) { this.eout('RTNETLINK answers: No such process\n'); return 2; } }
        return 0;
      }
      const order = st.routes.slice().sort((x, y) => (x.dst === 'default' ? -1 : 0) - (y.dst === 'default' ? -1 : 0));
      this.out(order.map(r => `${r.dst} ${r.via ? `via ${r.via} ` : ''}dev ${r.dev} proto ${r.proto} ${r.proto === 'kernel' ? `scope link src ${r.src} ` : ''}`).join('\n') + (order.length ? '\n' : ''));
      return 0;
    }
    if (/^(n|ne|neigh|neighbor|neighbour)$/.test(obj)) { this.out(Object.entries(st.neigh).map(([ip, mac]) => `${ip} dev enp0s3 lladdr ${mac} REACHABLE`).join('\n') + (Object.keys(st.neigh).length ? '\n' : '')); return 0; }
    this.eout(`Object "${obj}" is unknown, try "ip help".\n`); return 1;
  };
  World.prototype.uid = function () { const r = (this.node('/etc/passwd').data || '').split('\n').find(l => l.split(':')[0] === this.user); return r ? r.split(':')[2] : '1000'; };
  C.ping = function (a) {
    let n = 4, host = '';
    for (let i = 0; i < a.length; i++) { if (a[i] === '-c') n = +a[++i]; else if (/^-c\d+$/.test(a[i])) n = +a[i].slice(2); else if (a[i] === '-W' || a[i] === '-i' || a[i] === '-w') i++; else if (!a[i].startsWith('-')) host = a[i]; }
    if (!host) { this.eout('ping: usage error: Destination address required\n'); return 1; }
    const ip = this.resolve(host);
    if (!ip) { this.eout(`ping: ${host}: ${this.routeTo('192.168.1.1') ? 'Name or service not known' : 'Temporary failure in name resolution'}\n`); return 2; }
    const r = this.routeTo(ip); if (!r) { this.eout('ping: connect: Network is unreachable\n'); return 2; }
    const h = this.reach(ip), head = `PING ${host} (${ip}) 56(84) bytes of data.\n`, ms = this.clock;
    const tail = (rx, err) => `\n--- ${host} ping statistics ---\n${n} packets transmitted, ${rx} received, ${err ? `+${n} errors, ` : ''}${rx ? Math.round(100 - rx * 100 / n) : 100}% packet loss, time ${n > 1 ? (n - 1) * 1001 + (rx ? 2 : 49) : 0}ms\n`;
    this.clock += n * 1000;
    if (h.unreachable) { this.out(head + Array.from({ length: n }, (_, i) => `From ${r.src} icmp_seq=${i + 1} Destination Host Unreachable\n`).join('') + tail(0, true)); return 1; }
    if (h.lost) { this.out(head + tail(0)); return 1; }
    const t = Array.from({ length: n }, (_, i) => +(h.ms * (0.94 + ((i * 37 + ms) % 13) / 100)).toFixed(h.ms < 1 ? 3 : 1));
    const mn = Math.min(...t), mx = Math.max(...t), av = t.reduce((x, y) => x + y, 0) / n, md = Math.sqrt(t.reduce((x, y) => x + (y - av) ** 2, 0) / n);
    this.out(head + t.map((x, i) => `64 bytes from ${host === ip ? ip : `${host} (${ip})`}: icmp_seq=${i + 1} ttl=${h.ttl} time=${x} ms\n`).join('') + tail(n) + `rtt min/avg/max/mdev = ${[mn, av, mx, md].map(x => x.toFixed(3)).join('/')} ms\n`);
    return 0;
  };
  C.traceroute = C.tracepath = function (a) {
    const host = a.filter(x => !x.startsWith('-') && !/^\d+$/.test(x))[0], ip = host && this.resolve(host);
    if (!ip) { this.eout(`${host || ''}: Name or service not known\nCannot handle "host" cmdline arg \`${host || ''}' on position 1 (argc 1)\n`); return 2; }
    const h = this.reach(ip) || {}, hops = (h.hops || []).concat([ip]);
    this.out(`traceroute to ${host} (${ip}), 30 hops max, 60 byte packets\n` + hops.map((x, i) => ` ${i + 1}  ${x}  ${(0.4 + i * 3.8).toFixed(3)} ms`).join('\n') + '\n');
    return 0;
  };
  C.ss = function (a) {
    const f = a.join(' ').replace(/-/g, ''), tcp = /t/.test(f) || !/u/.test(f), udp = /u/.test(f), num = /n/.test(f), procs = /p/.test(f) && this.user === 'root';
    const name = p => num ? p : ({ 22: 'ssh', 53: 'domain', 80: 'http' })[p] || p;
    const L = this.listening().filter(l => (l.udp ? udp : tcp));
    const net1 = udp && tcp, sp = x => { const k = x.lastIndexOf(':'); return [x.slice(0, k), x.slice(k + 1)]; };
    const R = L.map(l => ({ id: l.udp ? 'udp' : 'tcp', st: l.udp ? 'UNCONN' : 'LISTEN', rq: '0', sq: String(l.udp ? 0 : l.q), la: l.addr, lp: String(name(l.port)), pa: l.addr.startsWith('[') ? '[::]' : '0.0.0.0', pp: '*', pr: procs ? `users:(("${l.prog}",pid=${l.pid},fd=${l.fd}))` : '' }));
    const wA = Math.max(13, ...R.map(r => r.la.length)), wP = Math.max(4, ...R.map(r => r.lp.length)), wB = Math.max(12, ...R.map(r => r.pa.length));
    const lead = (id, st, rq, sq) => (net1 ? id.padEnd(5) + ' ' : '') + st.padEnd(6) + ' ' + rq.padEnd(6) + ' ' + sq.padEnd(6) + ' ';
    this.out(lead('Netid', 'State', 'Recv-Q', 'Send-Q') + 'Local Address'.padStart(wA) + ':' + 'Port'.padEnd(wP) + ' ' + 'Peer Address'.padStart(wB) + ':' + 'Port'.padEnd(4) + 'Process\n' + R.map(r => (lead(r.id, r.st, r.rq, r.sq) + r.la.padStart(wA) + ':' + r.lp.padEnd(wP) + ' ' + r.pa.padStart(wB) + ':' + r.pp.padEnd(4) + ' ' + r.pr).replace(/\s+$/, '')).join('\n') + '\n');
    return 0;
  };
  C.curl = function (a) {
    let head = false, quiet = false, out = '', url = '';
    for (let i = 0; i < a.length; i++) { const x = a[i]; if (x === '-I' || x === '--head') head = true; else if (/^-[a-zA-Z]+$/.test(x) && x.includes('I')) { head = true; quiet = x.includes('s'); } else if (x === '-o') out = a[++i]; else if (/^-[a-zA-Z]+$/.test(x)) { if (x.includes('s')) quiet = true; } else url = x; }
    const m = /^(?:(https?):\/\/)?([^/:]+)(?::(\d+))?(\/.*)?$/.exec(url || '');
    if (!m) { this.eout('curl: (3) URL rejected: Malformed input to a URL function\n'); return 3; }
    const scheme = m[1] || 'http', host = m[2], port = +(m[3] || (scheme === 'https' ? 443 : 80)), ip = this.resolve(host);
    if (!ip) { this.eout(`curl: (6) Could not resolve host: ${host}\n`); return 6; }
    if (!this.routeTo(ip)) { this.eout(`curl: (7) Failed to connect to ${host} port ${port} after 0 ms: Couldn't connect to server\n`); return 7; }
    const h = this.reach(ip) || {};
    if (!h.ports || !h.ports.includes(port)) { this.eout(`curl: (7) Failed to connect to ${host} port ${port} after ${h.local ? 0 : Math.round(h.ms || 0)} ms: Couldn't connect to server\n`); return 7; }
    const d = new Date(this.clock), date = `${DAYS3[d.getUTCDay()]}, ${String(d.getUTCDate()).padStart(2, '0')} ${MON3[d.getUTCMonth()]} ${d.getUTCFullYear()} ${d.toISOString().slice(11, 19)} GMT`;
    const local = h.local, file = local ? (this.node('/var/www/html/index.html') || this.node('/var/www/html/index.nginx-debian.html')) : null, body = local ? (file ? file.data : '') : '<h1>shop.lab</h1>\n';
    if (scheme === 'https' && local) { this.eout(`curl: (7) Failed to connect to ${host} port 443 after 0 ms: Couldn't connect to server\n`); return 7; }
    const hdr = `HTTP/1.1 200 OK\r\nServer: nginx/1.24.0 (Ubuntu)\r\nDate: ${date}\r\nContent-Type: text/html\r\nContent-Length: ${enc(body)}\r\nLast-Modified: Mon, 09 Nov 2026 10:00:00 GMT\r\nConnection: keep-alive\r\nETag: "${(enc(body) * 7919).toString(16)}-${enc(body).toString(16)}"\r\nAccept-Ranges: bytes\r\n\r\n`.replace(/\r/g, '');
    if (head) { this.out(hdr); return 0; }
    if (out) { this.mk(this.abs(out), 'f', 0o664 & ~this.umask, this.user, body); const b = String(enc(body)); if (!quiet) this.eout(`  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n                                 Dload  Upload   Total   Spent    Left  Speed\n100 ${b.padStart(5)}  100 ${b.padStart(5)}    0     0   600k      0 --:--:-- --:--:-- --:--:--  600k\n`); return 0; }
    this.out(body); return 0;
  };
  C.nc = function (a) {
    const z = a.some(x => /^-[a-z]*z/.test(x)), v = a.some(x => /^-[a-z]*v/.test(x));
    const pos = a.filter((x, i) => !x.startsWith('-') && !(a[i - 1] === '-w')), host = pos[0], port = +pos[1];
    if (!z) { this.eout('The practice shell runs nc only with -z, to test whether a port is open: nc -zv HOST PORT\n'); return 1; }
    const ip = this.resolve(host || '');
    if (!ip) { this.eout(`nc: getaddrinfo for host "${host}" port ${port}: Name or service not known\n`); return 1; }
    const h = this.routeTo(ip) ? this.reach(ip) : null;
    if (h && h.ports && h.ports.includes(port)) { if (v) this.eout(`Connection to ${host} ${port} port [tcp/${SERVICES[port] || '*'}] succeeded!\n`); return 0; }
    if (v) this.eout(h && (h.local || h.mac || h.hops) ? `nc: connect to ${host} port ${port} (tcp) failed: Connection refused\n` : `nc: connect to ${host} port ${port} (tcp) timed out: Operation now in progress\n`);
    return 1;
  };
  World.prototype.dnsAnswer = function (name, type) {
    const st = this.net(), n = name.replace(/\.$/, '');
    if (type === 'MX') return st.mx[n] ? [[n + '.', 'MX', st.mx[n]]] : [];
    const d = st.dns[n]; return d ? [[n + '.', 'A', d[1]]] : [];
  };
  C.dig = function (a) {
    const short = a.includes('+short'), args = a.filter(x => !x.startsWith('+') && !x.startsWith('@'));
    const type = (args.find(x => /^(A|MX|AAAA|NS|TXT)$/i.test(x)) || 'A').toUpperCase(), name = args.find(x => !/^(A|MX|AAAA|NS|TXT)$/i.test(x)) || '.';
    if (!this.routeTo('192.168.1.1')) { this.out(`;; communications error to 127.0.0.53#53: timed out\n`); return 9; }
    const ans = this.dnsAnswer(name, type);
    if (short) { this.out(ans.map(r => r[2]).join('\n') + (ans.length ? '\n' : '')); return 0; }
    const ok = ans.length || this.net().dns[name.replace(/\.$/, '')];
    this.out(`\n; <<>> DiG 9.18.39-0ubuntu0.24.04.9-Ubuntu <<>> ${a.join(' ')}\n;; global options: +cmd\n;; Got answer:\n;; ->>HEADER<<- opcode: QUERY, status: ${ok ? 'NOERROR' : 'NXDOMAIN'}, id: ${(this.clock / 1000 | 0) % 65536}\n;; flags: qr rd ra; QUERY: 1, ANSWER: ${ans.length}, AUTHORITY: 0, ADDITIONAL: 1\n\n;; OPT PSEUDOSECTION:\n; EDNS: version: 0, flags:; udp: 65494\n;; QUESTION SECTION:\n;${name.replace(/\.?$/, '.')}\t\t\tIN\t${type}\n\n` + (ans.length ? `;; ANSWER SECTION:\n${ans.map(r => `${r[0]}\t\t300\tIN\t${r[1]}\t${r[2]}`).join('\n')}\n\n` : '') + `;; Query time: 3 msec\n;; SERVER: 127.0.0.53#53(127.0.0.53) (UDP)\n;; WHEN: ${new Date(this.clock).toUTCString().replace(/^(\w+), (\d+) (\w+) (\d+) ([\d:]+) GMT$/, '$1 $3 $2 $5 UTC $4')}\n;; MSG SIZE  rcvd: ${40 + name.length + ans.length * 16}\n\n`);
    return 0;
  };
  C.host = function (a) {
    const name = a.filter(x => !x.startsWith('-'))[0] || '';
    const A = this.dnsAnswer(name, 'A'), M = this.dnsAnswer(name, 'MX');
    if (!A.length && !M.length) { this.out(`Host ${name} not found: 3(NXDOMAIN)\n`); return 1; }
    this.out(A.map(r => `${name} has address ${r[2]}\n`).join('') + M.map(r => `${name} mail is handled by ${r[2]}\n`).join(''));
    return 0;
  };
  C.nslookup = function (a) {
    const name = a.filter(x => !x.startsWith('-'))[0] || '', A = this.dnsAnswer(name, 'A');
    this.out(`Server:\t\t127.0.0.53\nAddress:\t127.0.0.53#53\n\n` + (A.length ? `Non-authoritative answer:\n${A.map(r => `Name:\t${name}\nAddress: ${r[2]}`).join('\n')}\n\n` : `** server can't find ${name}: NXDOMAIN\n\n`));
    return A.length ? 0 : 1;
  };

  /* ---------- ssh: keys, known_hosts, ~/.ssh/config, a remote file server (files, 192.168.1.20) and sshd -t ---------- */
  const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  const prng = seed => { let h = 2166136261; for (const ch of String(seed)) h = Math.imul(h ^ ch.charCodeAt(0), 16777619) >>> 0; return () => { h ^= h << 13; h >>>= 0; h ^= h >>> 17; h ^= h << 5; h >>>= 0; return h; }; };
  const bytesOf = (seed, n) => { const r = prng(seed); return Array.from({ length: n }, () => r() & 255); };
  const b64 = bytes => { let o = ''; for (let i = 0; i < bytes.length; i += 3) { const [a, b = 0, c = 0] = bytes.slice(i, i + 3), n = (a << 16) | (b << 8) | c; o += B64[n >> 18 & 63] + B64[n >> 12 & 63] + (i + 1 < bytes.length ? B64[n >> 6 & 63] : '=') + (i + 2 < bytes.length ? B64[n & 63] : '='); } return o; };
  const fpOf = pub => 'SHA256:' + b64(bytesOf('fp' + pub, 32)).replace(/=+$/, '');
  const randomart = (fp, type, bits) => {
    const W = 17, H = 9, f = Array(W * H).fill(0), sym = ' .o+=*BOX@%&#/^SE', raw = bytesOf('fp' + fp, 32); let x = 8, y = 4;
    raw.forEach(b => { for (let k = 0; k < 4; k++) { x += (b & 1) ? 1 : -1; y += (b & 2) ? 1 : -1; x = Math.max(0, Math.min(W - 1, x)); y = Math.max(0, Math.min(H - 1, y)); f[y * W + x]++; b >>= 2; } });
    f[4 * W + 8] = 15; f[y * W + x] = 16;
    const top = `[${type} ${bits}]`, padL = Math.floor((W - top.length) / 2);
    const rows = []; for (let r = 0; r < H; r++) rows.push('|' + Array.from({ length: W }, (_, c) => { const v = f[r * W + c]; return v === 15 ? 'S' : v === 16 ? 'E' : sym[Math.min(v, 14)]; }).join('') + '|');
    return '+' + '-'.repeat(padL) + top + '-'.repeat(W - padL - top.length) + '+\n' + rows.join('\n') + '\n+----[SHA256]-----+\n';
  };
  const khPrefix = host => `|1|${b64(bytesOf('s' + host, 20))}|${b64(bytesOf('h' + host, 20))}`;
  const HOSTKEY = { files: 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFf1Lq2vY8bTzR0kXn3mPq7sWc5dHj9aUe4oKi6tBr2G' };
  World.prototype.remote = function () {
    if (!this.remoteState) this.remoteState = { keys: {}, files: {}, host: 'files', ip: '192.168.1.20' };
    return this.remoteState;
  };
  World.prototype.sshConfig = function (alias) {
    const n = this.node(this.abs('~/.ssh/config')), o = { HostName: alias };
    if (!n) return o;
    let on = false;
    for (const raw of n.data.split('\n')) {
      const l = raw.replace(/#.*/, '').trim(); if (!l) continue;
      const m = /^(\S+)\s*=?\s*(.*)$/.exec(l); if (!m) continue;
      const k = m[1].toLowerCase();
      if (k === 'host') { on = m[2].split(/\s+/).some(pat => new RegExp('^' + pat.replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*').replace(/\?/g, '.') + '$').test(alias)); continue; }
      if (on) { const key = { hostname: 'HostName', user: 'User', port: 'Port', identityfile: 'IdentityFile', stricthostkeychecking: 'StrictHostKeyChecking', proxyjump: 'ProxyJump' }[k]; if (key && (o[key] === undefined || (key === 'HostName' && o.HostName === alias && !o._hn))) { o[key] = m[2]; if (key === 'HostName') o._hn = true; } }
    }
    return o;
  };
  C['ssh-keygen'] = function (a) {
    let type = 'ed25519', bits = 0, file = '', pass = null, comment = `${this.user}@${HOST}`, quiet = false, list = false, remove = '';
    for (let i = 0; i < a.length; i++) { const x = a[i]; if (x === '-t') type = a[++i]; else if (x === '-b') bits = +a[++i]; else if (x === '-f') file = a[++i]; else if (x === '-N') pass = a[++i]; else if (x === '-C') comment = a[++i]; else if (x === '-q') quiet = true; else if (x === '-l') list = true; else if (x === '-R') remove = a[++i]; else if (x === '-lf') { list = true; file = a[++i]; } }
    const home = this.abs('~');
    if (remove) {
      const kh = this.abs(file || '~/.ssh/known_hosts'), n = this.node(kh);
      if (!n) { this.eout(`Cannot stat ${kh}: No such file or directory\n`); return 255; }
      const L = n.data.split('\n'), keep = [], tag = khPrefix(remove); let hit = 0;
      L.forEach((l, i) => { if (l.includes(tag)) { hit = i + 1; } else keep.push(l); });
      if (!hit) { this.out(`Host ${remove} not found in ${kh}\n`); return 0; }
      this.mk(kh + '.old', 'f', 0o600, this.user, n.data); n.data = keep.join('\n');
      this.out(`# Host ${remove} found: line ${hit}\n${kh} updated.\nOriginal contents retained as ${kh}.old\n`); return 0;
    }
    if (list) {
      const f = this.abs(file || '~/.ssh/id_ed25519.pub'), n = this.node(f) || this.node(f + '.pub');
      if (!n) { this.eout(`${file}: No such file or directory\n`); return 255; }
      const pub = /\.pub$/.test(f) || !n.data.startsWith('-----') ? n.data.trim() : (this.node(f + '.pub') || { data: '' }).data.trim();
      if (!/^ssh-|^ecdsa-/.test(pub)) { this.eout(`${file} is not a public key file.\n`); return 255; }
      const [t, , ...c] = pub.split(' '), T = t === 'ssh-ed25519' ? ['256', 'ED25519'] : t === 'ssh-rsa' ? [String(pub.length > 500 ? 4096 : 3072), 'RSA'] : ['256', 'ECDSA'];
      this.out(`${T[0]} ${fpOf(pub)} ${c.join(' ') || 'no comment'} (${T[1]})\n`); return 0;
    }
    if (!/^(ed25519|rsa|ecdsa)$/.test(type)) { this.eout(`unknown key type ${type}\n`); return 255; }
    if (!bits) bits = type === 'ed25519' ? 256 : type === 'rsa' ? 3072 : 256;
    const prompt = !file;
    if (!file) file = '~/.ssh/id_' + type;
    const f = this.abs(file), dir = dirName(f);
    const mkDot = () => { if (dir === home + '/.ssh' && !this.node(dir)) { this.mk(dir, 'd', 0o700, this.user, ''); if (!quiet) this.out(`Created directory '${dir}'.\n`); } };
    if (!prompt) mkDot();
    if (!quiet) this.out(`Generating public/private ${type} key pair.\n`);
    if (prompt) { this.out(`Enter file in which to save the key (${home}/.ssh/id_${type}): \n`); mkDot(); }
    if (!this.node(dir)) { this.eout(`Saving key "${f}" failed: No such file or directory\n`); return 255; }
    if (this.node(f)) { this.out(`${f} already exists.\nOverwrite (y/n)? \n`); return 1; }
    if (pass === null) this.out('Enter passphrase (empty for no passphrase): \nEnter same passphrase again: \n');
    const id = `${type}${f}${this.clock}`, keyB = type === 'ed25519' ? 'AAAAC3NzaC1lZDI1NTE5AAAAI' + b64(bytesOf(id, 32)).slice(0, 43) : type === 'rsa' ? 'AAAAB3NzaC1yc2EAAAADAQABAAABgQ' + b64(bytesOf(id, bits / 8 + 12)).replace(/=+$/, '') : 'AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBB' + b64(bytesOf(id, 63)).replace(/=+$/, '');
    const pub = `${type === 'ed25519' ? 'ssh-ed25519' : type === 'rsa' ? 'ssh-rsa' : 'ecdsa-sha2-nistp256'} ${keyB} ${comment}`;
    this.mk(f, 'f', 0o600, this.user, `-----BEGIN OPENSSH PRIVATE KEY-----\n${('b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW' + b64(bytesOf('priv' + id, 240)).replace(/=+$/, '')).slice(0, type === 'ed25519' ? 334 : 1000 + bits / 4).replace(/(.{70})/g, '$1\n')}\n-----END OPENSSH PRIVATE KEY-----\n`).mtime = this.now();
    this.node(f).sshPass = !!pass;
    this.mk(f + '.pub', 'f', 0o644, this.user, pub + '\n').mtime = this.now();
    if (!quiet) this.out(`Your identification has been saved in ${file === '~/.ssh/id_' + type && prompt ? f : file}\nYour public key has been saved in ${(file === '~/.ssh/id_' + type && prompt ? f : file)}.pub\nThe key fingerprint is:\n${fpOf(pub)} ${comment}\nThe key's randomart image is:\n${randomart(pub, type.toUpperCase(), bits)}`);
    return 0;
  };
  World.prototype.sshTarget = function (spec) {
    const [u, h0] = spec.includes('@') ? spec.split('@') : [null, spec], cfg = this.sshConfig(h0);
    return { user: u || cfg.User || this.user, alias: h0, host: cfg.HostName || h0, port: +(cfg.Port || 22), identity: cfg.IdentityFile, strict: cfg.StrictHostKeyChecking };
  };
  World.prototype.sshConnect = function (t, opts) {
    const ip = this.resolve(t.host);
    if (!ip) { this.eout(`ssh: Could not resolve hostname ${t.host}: Name or service not known\n`); return null; }
    const h = this.routeTo(ip) ? this.reach(ip) : null;
    if (!h || !h.ports || !h.ports.includes(t.port)) { this.eout(h && h.unreachable ? `ssh: connect to host ${t.host} port ${t.port}: No route to host\n` : h && (h.mac || h.local || h.hops) ? `ssh: connect to host ${t.host} port ${t.port}: Connection refused\n` : `ssh: connect to host ${t.host} port ${t.port}: Connection timed out\n`); return null; }
    if (ip !== '192.168.1.20') { this.eout(`${t.user}@${t.host}: Permission denied (publickey).\n`); return null; }
    const khf = this.abs('~/.ssh/known_hosts'), kh = this.node(khf), tag = khPrefix(t.host), hk = HOSTKEY.files;
    if (!kh || !kh.data.includes(tag)) {
      const strict = opts.strict || t.strict;
      if (strict === 'yes') { this.eout(`No ED25519 host key is known for ${t.host} and you have requested strict checking.\nHost key verification failed.\n`); return null; }
      if (strict !== 'accept-new' && strict !== 'no') this.out(`The authenticity of host '${t.host} (${ip})' can't be established.\nED25519 key fingerprint is ${fpOf(hk)}.\nThis key is not known by any other names.\nAre you sure you want to continue connecting (yes/no/[fingerprint])? yes\n`);
      this.eout(`Warning: Permanently added '${t.host}' (ED25519) to the list of known hosts.\n`);
      if (!this.node(this.abs('~/.ssh'))) this.mk(this.abs('~/.ssh'), 'd', 0o700, this.user, '');
      const line = `${tag} ${hk.split(' ').slice(0, 2).join(' ')}`;
      if (kh) kh.data = kh.data.replace(/\n?$/, '\n') + line + '\n'; else this.mk(khf, 'f', 0o600, this.user, line + '\n');
    }
    return { ip, hk };
  };
  World.prototype.sshAuth = function (t, ident) {
    const R = this.remote(), cands = (ident ? [ident] : t.identity ? [t.identity] : ['~/.ssh/id_ed25519', '~/.ssh/id_ecdsa', '~/.ssh/id_rsa']).map(x => this.abs(x));
    for (const f of cands) {
      const n = this.node(f), pub = this.node(f + '.pub');
      if (!n) continue;
      if (n.mode & 0o077) { this.eout(`@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\nPermissions 0${(n.mode & 0o777).toString(8)} for '${f.replace(this.abs('~'), '~').replace(/^~/, this.abs('~'))}' are too open.\nIt is required that your private key files are NOT accessible by others.\nThis private key will be ignored.\nLoad key "${f}": bad permissions\n`); continue; }
      if (pub && (R.keys[t.user] || []).includes(pub.data.trim())) return true;
    }
    return false;
  };
  const REMOTE_RUN = (w, t, cmd) => {
    const R = w.remote(), home = t.user === 'root' ? '/root' : '/home/' + t.user, mine = Object.keys(R.files).filter(k => k.startsWith(home + '/')).map(k => k.slice(home.length + 1)).sort();
    const out = [];
    for (const part of cmd.split(/\s*;\s*|\s*&&\s*/)) {
      const [c, ...x] = part.trim().split(/\s+/);
      if (!c) continue;
      if (c === 'hostname') out.push('files');
      else if (c === 'whoami') out.push(t.user);
      else if (c === 'uptime') out.push(' 09:31:00 up 12 days,  3:04,  1 user,  load average: 0.02, 0.04, 0.01');
      else if (c === 'ls') out.push(...mine.filter(k => !k.startsWith('.')));
      else if (c === 'cat' && x[0]) { const p = x[0].replace(/^~\//, home + '/').replace(/^(?!\/)/, home + '/'); if (/authorized_keys$/.test(p)) out.push(...(R.keys[t.user] || [])); else if (R.files[p] !== undefined) out.push(R.files[p].replace(/\n$/, '')); else { w.eout(`cat: ${x[0]}: No such file or directory\n`); return 1; } }
      else if (c === 'id') out.push(`uid=1000(${t.user}) gid=1000(${t.user}) groups=1000(${t.user})`);
      else { w.eout(`bash: line 1: ${c}: the practice file server only runs hostname, whoami, uptime, id, ls and cat\n`); return 127; }
    }
    if (out.length) w.out(out.join('\n') + '\n');
    return 0;
  };
  C.ssh = function (a) {
    let ident = '', port = 0, strict = '', i = 0, verbose = false; const rest = [];
    for (; i < a.length; i++) { const x = a[i]; if (x === '-i') ident = a[++i]; else if (x === '-p') port = +a[++i]; else if (x === '-o') { const m = /^StrictHostKeyChecking=(\S+)$/i.exec(a[++i] || ''); if (m) strict = m[1]; } else if (x === '-v') verbose = true; else if (/^-[LRDJFlTt]$/.test(x)) { if (x !== '-T' && x !== '-t') i++; } else if (x.startsWith('-') && !rest.length) { } else { rest.push(...a.slice(i)); break; } }
    if (!rest.length) { this.eout('usage: ssh [-46AaCfGgKkMNnqsTtVvXxYy] [-B bind_interface] [-b bind_address]\n           [-c cipher_spec] [-D [bind_address:]port] [-E log_file]\n           [-e escape_char] [-F configfile] [-I pkcs11] [-i identity_file]\n           [-J destination] [-L address] [-l login_name] [-m mac_spec]\n           [-O ctl_cmd] [-o option] [-P tag] [-p port] [-R address]\n           [-S ctl_path] [-W host:port] [-w local_tun[:remote_tun]]\n           destination [command [argument ...]]\n'); return 255; }
    const t = this.sshTarget(rest[0]); if (port) t.port = port; void verbose;
    const c = this.sshConnect(t, { strict }); if (!c) return 255;
    if (!this.sshAuth(t, ident)) { this.out(`${t.user}@${t.host}'s password: \n`); this.eout(`The practice shell cannot type passwords. Log in with a key: create one with ssh-keygen, then install it with ssh-copy-id ${rest[0]}.\n`); return 255; }
    const cmd = rest.slice(1).join(' ');
    if (!cmd) { this.out(`Welcome to Ubuntu 24.04.1 LTS (GNU/Linux 6.8.0-49-generic x86_64)\n\nLast login: Mon Nov 23 08:12:44 2026 from 192.168.1.50\n`); this.eout(`The practice shell does not open remote sessions. Put the command on the line instead, for example: ssh ${rest[0]} hostname\nConnection to ${t.host} closed.\n`); return 0; }
    return REMOTE_RUN(this, t, cmd);
  };
  C['ssh-copy-id'] = function (a) {
    let ident = '', strict = ''; const rest = [];
    for (let i = 0; i < a.length; i++) { if (a[i] === '-i') ident = a[++i]; else if (a[i] === '-o') { const m = /^StrictHostKeyChecking=(\S+)$/i.exec(a[++i] || ''); if (m) strict = m[1]; } else if (!a[i].startsWith('-')) rest.push(a[i]); }
    if (!rest.length) { this.eout('Usage: /usr/bin/ssh-copy-id [-h|-?|-f|-n|-s|-x] [-i [identity_file]] [-p port] [-F alternative ssh_config file] [-t target_path] [[-o <ssh -o options>] ...] [user@]hostname\n'); return 1; }
    const f = this.abs(ident ? ident.replace(/(\.pub)?$/, '.pub') : '~/.ssh/id_ed25519.pub'), n = this.node(f);
    if (!n) { this.eout(`/usr/bin/ssh-copy-id: ERROR: failed to open ID file '${f.replace(/\.pub$/, '')}': No such file or directory\n`); return 1; }
    this.eout(`/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "${f}"\n`);
    const t = this.sshTarget(rest[0]), c = this.sshConnect(t, { strict }); if (!c) return 1;
    const R = this.remote(), list = R.keys[t.user] = R.keys[t.user] || [], key = n.data.trim();
    this.eout('/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed\n');
    if (list.includes(key)) { this.eout(`\n/usr/bin/ssh-copy-id: WARNING: All keys were skipped because they already exist on the remote system.\n\t\t(if you think this is a mistake, you may want to use -f option)\n\n`); return 0; }
    this.eout('/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys\n');
    this.out(`${t.user}@${t.host}'s password: \n\nNumber of key(s) added: 1\n\nNow try logging into the machine, with:   "ssh '${rest[0]}'"\nand check to make sure that only the key(s) you wanted were added.\n\n`);
    list.push(key);
    return 0;
  };
  C.scp = function (a) {
    const args = a.filter(x => !x.startsWith('-')), [src, dst] = args.slice(-2);
    if (!src || !dst) { this.eout('usage: scp [-346ABCOpqRrsTv] [-c cipher] [-D sftp_server_path] [-F ssh_config]\n           [-i identity_file] [-J destination] [-l limit] [-o ssh_option]\n           [-P port] [-S program] [-X sftp_option] source ... target\n'); return 255; }
    const remoteOf = x => { const m = /^([^/:]+):(.*)$/.exec(x); return m ? { spec: m[1], path: m[2] } : null; };
    const rs = remoteOf(src), rd = remoteOf(dst);
    if (!rs && !rd) { return C.cp.call(this, [src, dst]); }
    const r = rd || rs, t = this.sshTarget(r.spec), c = this.sshConnect(t, {}); if (!c) return 255;
    if (!this.sshAuth(t, '')) { this.out(`${t.user}@${t.host}'s password: \n`); this.eout('The practice shell cannot type passwords. Install a key with ssh-copy-id first.\n'); return 255; }
    const R = this.remote(), home = '/home/' + t.user, rpath = p => (p || '').replace(/^~\/?/, home + '/').replace(/^(?!\/)/, home + '/').replace(/\/$/, '');
    if (rd) {
      const n = this.node(this.abs(src)); if (!n || n.type !== 'f') { this.eout(`scp: stat local "${src}": No such file or directory\n`); return 255; }
      let p = rpath(rd.path); if (p === home || rd.path === '' || rd.path.endsWith('/')) p = (p === home ? home : p) + '/' + baseName(src);
      R.files[p] = n.data; const sz = enc(n.data);
      this.out(`${baseName(src).padEnd(50)} 100% ${String(sz).padStart(4)}    ${(sz / 1024 * 0.97).toFixed(1)}KB/s   00:00\n`); return 0;
    }
    const p = rpath(rs.path); if (R.files[p] === undefined) { this.eout(`scp: ${rs.path}: No such file or directory\n`); return 1; }
    let d = this.abs(dst); const dn = this.node(d); if (dn && dn.type === 'd') d = d.replace(/\/$/, '') + '/' + baseName(p);
    this.mk(d, 'f', 0o644 & ~this.umask, this.user, R.files[p]); this.out(`${baseName(p).padEnd(50)} 100% ${String(enc(R.files[p])).padStart(4)}    1.0KB/s   00:00\n`); return 0;
  };
  const SSHD_OPTS = 'port listenaddress addressfamily hostkey permitrootlogin passwordauthentication pubkeyauthentication kbdinteractiveauthentication challengeresponseauthentication usepam x11forwarding printmotd acceptenv subsystem include allowusers allowgroups denyusers denygroups maxauthtries maxsessions logingracetime clientaliveinterval clientalivecountmax permitemptypasswords allowtcpforwarding allowagentforwarding authorizedkeysfile loglevel syslogfacility banner match forcecommand chrootdirectory gatewayports permittunnel usedns compression authenticationmethods strictmodes tcpkeepalive pidfile'.split(' ');
  C.sshd = function (a) {
    if (!a.includes('-t') && !a.includes('-T')) { this.eout('sshd re-exec requires execution with an absolute path\n'); return 255; }
    if (this.user !== 'root') { this.eout('sshd: no hostkeys available -- exiting.\n'); return 1; }
    const cf = '/etc/ssh/sshd_config', n = this.node(cf); let bad = 0;
    n.data.split('\n').forEach((l, i) => { const t = l.replace(/#.*/, '').trim(); if (!t) return; const k = t.split(/[\s=]+/)[0].toLowerCase(); if (!SSHD_OPTS.includes(k)) { this.eout(`${cf}: line ${i + 1}: Bad configuration option: ${t.split(/[\s=]+/)[0]}\n`); bad++; } else if (k === 'permitrootlogin' && !/^(yes|no|prohibit-password|without-password|forced-commands-only)$/i.test(t.split(/[\s=]+/)[1] || '')) { this.eout(`${cf} line ${i + 1}: unsupported option "${t.split(/[\s=]+/)[1] || ''}".\n`); bad++; } else if (/^(passwordauthentication|pubkeyauthentication|usepam|x11forwarding)$/.test(k) && !/^(yes|no)$/i.test(t.split(/[\s=]+/)[1] || '')) { this.eout(`${cf} line ${i + 1}: unsupported option "${t.split(/[\s=]+/)[1] || ''}".\n`); bad++; } });
    if (bad) { this.eout(`${cf}: terminating, ${bad} bad configuration options\n`); return 255; }
    return 0;
  };

  /* ---------- ufw: rules, defaults and status as ufw 0.36 on Ubuntu 24.04 prints them (IPv6 on, as by default) ---------- */
  const UFW_APPS = { OpenSSH: '22/tcp', 'Nginx Full': '80,443/tcp', 'Nginx HTTP': '80/tcp', 'Nginx HTTPS': '443/tcp' };
  World.prototype.ufw = function () { if (!this.ufwState) this.ufwState = { on: false, def: { incoming: 'deny', outgoing: 'allow', routed: 'disabled' }, rules: [] }; return this.ufwState; };
  C.ufw = function (a0) {
    if (this.user !== 'root') { this.eout('ERROR: You need to be root to run this script\n'); return 1; }
    const st = this.ufw(), force = a0.includes('--force'), a = a0.filter(x => x !== '--force'), cmd = a[0] || '';
    const v6ok = from => from === 'Anywhere' || /:/.test(from);
    const parse = w => {
      let action = w[0].toUpperCase(), i = 1, dir = 'IN', to = '', from = 'Anywhere', port = '', proto = '';
      if (w[i] === 'in' || w[i] === 'out') { dir = w[i].toUpperCase(); i++; }
      if (w[i] === 'from') { from = w[i + 1] === 'any' ? 'Anywhere' : w[i + 1]; i += 2; if (w[i] === 'to') { i += 2; } if (w[i] === 'port') { port = w[i + 1]; i += 2; } if (w[i] === 'proto') { proto = w[i + 1]; i += 2; } to = port ? port + (proto ? '/' + proto : '') : 'Anywhere'; }
      else if (w[i] === 'to') { i += 2; if (w[i] === 'port') { port = w[i + 1]; i += 2; } if (w[i] === 'proto') { proto = w[i + 1]; i += 2; } to = port + (proto ? '/' + proto : ''); }
      else { const spec = w.slice(i).join(' '); if (UFW_APPS[spec]) to = spec; else if (/^\d+(:\d+)?(,\d+)*(\/(tcp|udp))?$/.test(spec) && spec.split(/[/,:]/).filter(x => /^\d+$/.test(x)).every(x => +x > 0 && +x < 65536)) to = spec; else if (/^\d+/.test(spec)) return { err: 'ERROR: Bad port' }; else return { err: `ERROR: Could not find a profile matching '${spec}'` }; }
      if (port && port.split(/[,:]/).some(x => !(+x > 0 && +x < 65536))) return { err: 'ERROR: Bad port' };
      if (!['ALLOW', 'DENY', 'REJECT', 'LIMIT'].includes(action)) return { err: `ERROR: Invalid syntax` };
      return { action, dir, to, from };
    };
    const same = (x, y) => x.action === y.action && x.dir === y.dir && x.to === y.to && x.from === y.from;
    const list = () => { const v4 = st.rules.filter(r => !r.no4).map(r => ({ r, v6: false })), v6 = st.rules.filter(r => v6ok(r.from) && !r.no6).map(r => ({ r, v6: true })); return v4.concat(v6); };
    const label = (r, v6, verbose) => { const t = r.to === 'Anywhere' ? 'Anywhere' : (verbose && UFW_APPS[r.to] ? `${UFW_APPS[r.to]} (${r.to})` : r.to); return v6 ? (t === 'Anywhere' ? 'Anywhere (v6)' : t.replace(/ \((.+)\)$/, ' ($1 (v6))').replace(/^([^ (]+)$/, '$1 (v6)')) : t; };
    const table = (numbered, verbose) => {
      const L = list(); if (!L.length) return '';
      const rows = L.map(({ r, v6 }, i) => (numbered ? `[${String(i + 1).padStart(2)}] ` : '') + label(r, v6, verbose).padEnd(27) + ((numbered || verbose) ? (r.action + ' ' + r.dir) : r.action).padEnd(12) + (v6 ? (r.from === 'Anywhere' ? 'Anywhere (v6)' : r.from) : r.from).padEnd(26));
      const pad = numbered ? '     ' : '';
      return `\n${pad}To                         Action      From\n${pad}--                         ------      ----\n${rows.join('\n')}\n\n`;
    };
    if (cmd === 'status') {
      if (!st.on) { this.out('Status: inactive\n'); return 0; }
      if (a[1] === 'verbose') { this.out(`Status: active\nLogging: on (low)\nDefault: ${st.def.incoming} (incoming), ${st.def.outgoing} (outgoing), ${st.def.routed} (routed)\nNew profiles: skip\n${table(false, true)}`); return 0; }
      this.out('Status: active\n' + table(a[1] === 'numbered', false)); return 0;
    }
    if (cmd === 'enable') { if (!force) this.out('Command may disrupt existing ssh connections. Proceed with operation (y|n)? y\n'); st.on = true; this.out('Firewall is active and enabled on system startup\n'); return 0; }
    if (cmd === 'disable') { st.on = false; this.out('Firewall stopped and disabled on system startup\n'); return 0; }
    if (cmd === 'reload') { this.out(st.on ? 'Firewall reloaded\n' : 'Firewall not enabled (skipping reload)\n'); return 0; }
    if (cmd === 'reset') { if (!force) this.out('Resetting all rules to installed defaults. Proceed with operation (y|n)? y\n'); const ts = new Date(this.clock).toISOString().slice(0, 19).replace(/-|:/g, '').replace('T', '_'); this.out(['user', 'before', 'after', 'user6', 'before6', 'after6'].map(f => `Backing up '${f}.rules' to '/etc/ufw/${f}.rules.${ts}'\n`).join('') + '\n'); st.on = false; st.rules = []; st.def = { incoming: 'deny', outgoing: 'allow', routed: 'disabled' }; return 0; }
    if (cmd === 'default') { const pol = a[1], d = a[2]; if (!/^(allow|deny|reject)$/.test(pol || '') || !/^(incoming|outgoing|routed)$/.test(d || '')) { this.eout('ERROR: Invalid syntax\n'); return 1; } st.def[d] = pol; this.out(`Default ${d} policy changed to '${pol}'\n(be sure to update your rules accordingly)\n`); return 0; }
    if (cmd === 'app') { if (a[1] === 'list') { this.out('Available applications:\n' + Object.keys(UFW_APPS).sort().map(k => '  ' + k).join('\n') + '\n'); return 0; } if (a[1] === 'info' && UFW_APPS[a.slice(2).join(' ')]) { const n = a.slice(2).join(' '); this.out(`Profile: ${n}\nTitle: ${n === 'OpenSSH' ? 'Secure shell server, an rshd replacement' : 'Web Server'}\nDescription: ${n === 'OpenSSH' ? 'OpenSSH is a free implementation of the Secure Shell protocol.' : 'Small, but very powerful and efficient web server'}\n\nPort${/,/.test(UFW_APPS[n]) ? 's' : ''}:\n  ${UFW_APPS[n]}\n`); return 0; } }
    if (cmd === 'delete') {
      if (/^\d+$/.test(a[1] || '')) { const L = list(), k = +a[1] - 1; if (!L[k]) { this.eout(`ERROR: Could not find rule '${a[1]}'\n`); return 1; } if (!force) { const q = L[k].r, m = /^(\d[\d,:]*)\/(tcp|udp)$/.exec(q.to); this.out(`Deleting:\n ${q.action.toLowerCase()} ${q.from === 'Anywhere' ? q.to : 'from ' + q.from + (q.to === 'Anywhere' ? '' : m ? ` to any port ${m[1]} proto ${m[2]}` : ` to any port ${q.to}`)}\nProceed with operation (y|n)? y\n`); } const q = L[k].r; if (L[k].v6) q.no6 = true; else q.no4 = true; if (q.no4 && (q.no6 || !v6ok(q.from))) st.rules.splice(st.rules.indexOf(q), 1); this.out(L[k].v6 ? 'Rule deleted (v6)\n' : 'Rule deleted\n'); return 0; }
      const r = parse(a.slice(1)); if (r.err) { this.eout(r.err + '\n'); return 1; } const k = st.rules.findIndex(x => same(x, r)); if (k < 0) { this.out('Could not delete non-existent rule\n' + (v6ok(r.from) ? 'Could not delete non-existent rule (v6)\n' : '')); return 0; } st.rules.splice(k, 1); this.out('Rule deleted\n' + (v6ok(r.from) ? 'Rule deleted (v6)\n' : '')); return 0;
    }
    let at = -1, w = a;
    if (cmd === 'insert') { at = +a[1] - 1; w = a.slice(2); if (!(at >= 0) || at > st.rules.length) { this.eout(`ERROR: Invalid position '${a[1]}'\n`); return 1; } }
    if (/^(allow|deny|reject|limit)$/.test(w[0] || '')) {
      const r = parse(w); if (r.err) { this.eout(r.err + '\n'); return 1; }
      if (st.rules.some(x => same(x, r))) { this.out(at >= 0 ? 'Skipping inserting existing rule\n' : 'Skipping adding existing rule\n' + (v6ok(r.from) ? 'Skipping adding existing rule (v6)\n' : '')); return 0; }
      if (at >= 0) st.rules.splice(at, 0, r); else st.rules.push(r);
      const word = at >= 0 ? 'Rule inserted' : st.on ? 'Rule added' : 'Rules updated'; this.out(word + '\n' + (v6ok(r.from) ? word + ' (v6)\n' : ''));
      return 0;
    }
    this.eout('ERROR: Invalid syntax\n\nUsage: ufw COMMAND\n'); return 1;
  };

  /* ---------- inodes, link counts and a live /proc built from the process table ---------- */
  World.prototype.ino = function (n) {
    if (n === this.root) return 2;
    if (!n.ino) n.ino = n.proc ? 40000 + (this.procIno = (this.procIno || 0) + 1) : (this.inoNext = (this.inoNext || 1310721) + 7);
    return n.ino;
  };
  World.prototype.links = function (n) {
    if (n.type === 'd') return Object.keys(n.kids).filter(k => n.kids[k].type === 'd').length + 2;
    let c = 0; const walk = d => { for (const k in d.kids) { const m = d.kids[k]; if (m === n) c++; if (m.type === 'd' && !m.proc && k !== 'proc') walk(m); } };
    walk(this.root); return Math.max(c, 1);
  };
  C.nproc = function () { this.out('2\n'); return 0; };
  const CAP_ALL = '000001ffffffffff';
  World.prototype.procFs = function () {
    const proc = this.root.kids.proc, keep = {}; if (!proc || !this.procs) return;
    for (const k in proc.kids) if (!proc.kids[k].proc) keep[k] = proc.kids[k];
    const self = this.nextPid, me = this.user;
    const F = (data, mode = 0o444, owner = 'root') => ({ type: 'f', name: '', mode, owner, group: owner, mtime: this.clock, data, proc: true });
    const L = (target, owner = 'root', mode = 0o777) => ({ type: 'l', name: '', mode, owner, group: owner, mtime: this.clock, target, proc: true });
    const D = (kids, mode = 0o555, owner = 'root') => { const n = { type: 'd', name: '', mode, owner, group: owner, mtime: this.clock, kids, proc: true }; for (const k in kids) kids[k].name = k; return n; };
    const ids = u => { const r = this.pwRow(u); return r ? [r[2], r[3]] : ['1000', '1000']; };
    const rows = this.procs.concat([{ pid: self, ppid: 2001, user: me, cmd: this.cmdNameReal || 'cat', comm: this.cmdNameReal || 'cat', stat: 'R', self: true }]);
    const kids = Object.assign({}, keep);
    for (const p of rows) {
      const name = (p.comm || baseName(p.cmd.split(' ')[0]).replace(/:$/, '')).slice(0, 15), [uid, gid] = ids(p.user), root = p.user === 'root';
      const state = p.self ? 'R (running)' : p.stat === 'T' ? 'T (stopped)' : p.stat === 'Z' ? 'Z (zombie)' : 'S (sleeping)';
      const virt = p.pid === 1 ? 167700 : 8000 + p.pid % 900 * 7, rss = 3000 + p.pid % 700 * 3;
      const tty = p.pid === 2001 || p.ppid === 2001;
      const status = `Name:\t${name}\nUmask:\t0022\nState:\t${state}\nTgid:\t${p.pid}\nNgid:\t0\nPid:\t${p.pid}\nPPid:\t${p.ppid}\nTracerPid:\t0\nUid:\t${uid}\t${uid}\t${uid}\t${uid}\nGid:\t${gid}\t${gid}\t${gid}\t${gid}\nFDSize:\t${tty ? 256 : 64}\nGroups:\t${root ? '' : '27 ' + gid + ' '}\nVmPeak:\t${pad(virt + 120, 8)} kB\nVmSize:\t${pad(virt, 8)} kB\nVmRSS:\t${pad(rss, 8)} kB\nVmSwap:\t       0 kB\nThreads:\t1\nCapInh:\t0000000000000000\nCapPrm:\t${root ? CAP_ALL : '0000000000000000'}\nCapEff:\t${root ? CAP_ALL : '0000000000000000'}\nCapBnd:\t${CAP_ALL}\nCapAmb:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t0\n`;
      const exe = p.pid === 1 ? '/usr/lib/systemd/systemd' : p.self ? (this.lookup(p.comm) ? this.lookup(p.comm).path : '/usr/bin/' + p.comm) : name === 'sshd' ? '/usr/sbin/sshd' : name === 'nginx' ? '/usr/sbin/nginx' : name === 'cron' ? '/usr/sbin/cron' : name === 'bash' ? '/usr/bin/bash' : '/usr/bin/' + name;
      const fds = tty ? { 0: L('/dev/pts/0', p.user, 0o700), 1: L('/dev/pts/0', p.user, 0o700), 2: L('/dev/pts/0', p.user, 0o700) } : { 0: L('/dev/null', p.user, 0o500), 1: L('socket:[21307]', p.user, 0o700), 2: L('socket:[21307]', p.user, 0o700) };
      if (p.pid === 2001) fds[255] = L('/dev/pts/0', p.user, 0o700);
      if (name === 'sshd') { fds[3] = L('socket:[22941]', 'root', 0o700); fds[4] = L('socket:[22943]', 'root', 0o700); }
      if (name === 'nginx' && p.pid === 905) { fds[6] = L('socket:[24518]', 'root', 0o700); fds[7] = L('socket:[24519]', 'root', 0o700); }
      if (p.self && this.procFd) Object.assign(fds, this.procFd(p.user, L));
      const env = (p.pid === 2001 || p.self) ? [...this.exported].filter(k => this.vars[k] !== undefined).map(k => k + '=' + this.vars[k]).join('\0') + '\0' : '';
      const cg = p.pid === 1 ? '/init.scope' : p.user === 'root' || p.user === 'www-data' ? `/system.slice/${name === 'sshd' ? 'ssh' : name}.service` : '/user.slice/user-1000.slice/session-3.scope';
      kids[p.pid] = D({ cgroup: F(`0::${cg}\n`, 0o444, p.user), oom_score_adj: F('0\n', 0o644, p.user), status: F(status, 0o444, p.user), comm: F(name + '\n', 0o644, p.user), cmdline: F(p.cmd.replace(/^-bash$/, '-bash').split(' ').join('\0') + '\0', 0o444, p.user),
        environ: F(env, 0o400, p.user), cwd: L(p.self || p.pid === 2001 ? this.cwd : '/', p.user), exe: L(exe, p.user), fd: D(fds, 0o500, p.user),
        ns: D(Object.fromEntries(['cgroup', 'ipc', 'mnt', 'net', 'pid', 'user', 'uts'].map((k, i) => [k, L(`${k}:[40265318${30 + i}]`, p.user)])), 0o511, p.user) }, 0o555, p.user);
    }
    kids.self = L(String(self));
    const total = 8048304, free = 3142212, avail = 5563880, cached = 2389412, buffers = 315556, swk = this.disks ? this.disks().swaps.reduce((t, x) => t + x.size / 1024 - 4, 0) : 0;
    kids.meminfo = F(`MemTotal:       ${pad(total, 8)} kB\nMemFree:        ${pad(free, 8)} kB\nMemAvailable:   ${pad(avail, 8)} kB\nBuffers:        ${pad(buffers, 8)} kB\nCached:         ${pad(cached, 8)} kB\nSwapCached:            0 kB\nActive:         ${pad(2650120, 8)} kB\nInactive:       ${pad(1498200, 8)} kB\nSwapTotal:      ${pad(swk, 8)} kB\nSwapFree:       ${pad(swk, 8)} kB\nDirty:                88 kB\nAnonPages:      ${pad(1442060, 8)} kB\nMapped:         ${pad(412300, 8)} kB\nShmem:          ${pad(122880, 8)} kB\nSlab:           ${pad(301240, 8)} kB\nPageTables:     ${pad(14320, 8)} kB\nCommitLimit:    ${pad(Math.floor(total / 2) + swk, 8)} kB\nCommitted_AS:   ${pad(3920400, 8)} kB\nHugePages_Total:       0\nHugepagesize:       2048 kB\n`);
    const running = rows.filter(r => r.self || r.cpu).length;
    kids.loadavg = F(`0.42 0.35 0.30 ${running}/${rows.length + 112} ${self}\n`);
    kids.uptime = F(`${(268860 + (this.clock - T0) / 1000).toFixed(2)} 530214.88\n`);
    kids.filesystems = F('nodev\tsysfs\nnodev\ttmpfs\nnodev\tbdev\nnodev\tproc\nnodev\tcgroup2\nnodev\tdevtmpfs\nnodev\tdebugfs\nnodev\tsecurityfs\nnodev\tsockfs\nnodev\tpipefs\nnodev\tdevpts\n\text4\nnodev\tsquashfs\n\tvfat\nnodev\tmqueue\n\txfs\nnodev\toverlay\n');
    kids.cmdline = F('BOOT_IMAGE=/boot/vmlinuz-6.8.0-practice root=UUID=b6e1c2a4-77aa-4e0f-9d3b-2f1c8a5e0d71 ro quiet\n');
    const tree = {};
    for (const [k, val] of Object.entries(this.sysctls())) { const parts = k.split('.'); let t = tree; parts.slice(0, -1).forEach(x => { t = t[x] = t[x] || {}; }); t[parts[parts.length - 1]] = val; }
    const mkTree = t => D(Object.fromEntries(Object.entries(t).map(([k, x]) => [k, typeof x === 'string' ? F(x + '\n', /^(ostype|osrelease)$/.test(k) ? 0o444 : 0o644) : mkTree(x)])));
    kids.sys = mkTree(tree);
    for (const k in kids) kids[k].name = k;
    proc.kids = kids;
  };

  /* the mount a path lives on, for cross-device checks */
  World.prototype.mountOf = function (path) {
    const dirs = this.disks().mounts.map(m => m.dir).concat(['/dev/shm', '/proc', '/run']);
    return dirs.filter(d => path === d || path.startsWith(d === '/' ? '/' : d + '/')).sort((x, y) => y.length - x.length)[0] || '/';
  };
  /* realpath: follow every symbolic link. The last part may be missing, as with readlink -f */
  World.prototype.canon = function (path, depth = 0) {
    const parts = norm(path).split('/').filter(Boolean); let cur = '/';
    for (let i = 0; i < parts.length; i++) {
      const next = norm(cur + '/' + parts[i]), n = this.node(next, false);
      if (!n) return i === parts.length - 1 ? next : null;
      if (n.type === 'l') { if (depth > 40) return null; const t = n.target.startsWith('/') ? n.target : cur + '/' + n.target; const r = this.canon(t, depth + 1); if (r === null) return null; cur = r; } else cur = next;
    }
    return cur;
  };
  C.mkfifo = function (a) {
    const [, rest] = opts(a, 'm');
    if (!rest.length) { this.eout('mkfifo: missing operand\n'); return 1; }
    for (const t of rest) {
      const p = this.abs(t);
      if (this.node(p, false)) { this.eout(`mkfifo: cannot create fifo '${t}': File exists\n`); return 1; }
      if (!this.node(dirName(p))) { this.eout(`mkfifo: cannot create fifo '${t}': No such file or directory\n`); return 1; }
      this.mk(p, 'p', 0o666 & ~this.umask, this.user, '').mtime = this.now();
    }
    return 0;
  };

  /* kernel settings shared by /proc/sys and sysctl */
  World.prototype.sysctls = function () {
    if (!this.sysctlState) this.sysctlState = { 'fs.file-max': '9223372036854775807', 'fs.protected_hardlinks': '1', 'fs.protected_symlinks': '1', 'kernel.dmesg_restrict': '1', 'kernel.hostname': HOST, 'kernel.kptr_restrict': '1', 'kernel.osrelease': '6.8.0-practice', 'kernel.ostype': 'Linux', 'kernel.pid_max': '4194304', 'kernel.randomize_va_space': '2', 'kernel.threads-max': '63318', 'net.ipv4.conf.all.accept_redirects': '1', 'net.ipv4.conf.all.rp_filter': '2', 'net.ipv4.ip_forward': '0', 'net.ipv4.tcp_syncookies': '1', 'vm.dirty_background_ratio': '10', 'vm.dirty_expire_centisecs': '3000', 'vm.dirty_ratio': '20', 'vm.overcommit_memory': '0', 'vm.overcommit_ratio': '50', 'vm.swappiness': '60', 'vm.vfs_cache_pressure': '100' };
    return this.sysctlState;
  };
  C.sysctl = function (a) {
    const st = this.sysctls(); let n = false, w = false, all = false, code = 0; const keys = [];
    for (const x of a) { if (x === '-n') n = true; else if (x === '-w') w = true; else if (x === '-a' || x === '-A' || x === '-X') all = true; else if (x === '--system' || x === '-p') { this.out(x === '-p' ? '' : '* Applying /usr/lib/sysctl.d/50-pid-max.conf ...\nkernel.pid_max = 4194304\n* Applying /etc/sysctl.d/99-sysctl.conf ...\n* Applying /etc/sysctl.conf ...\n'); return 0; } else keys.push(x); }
    if (all) { this.out(Object.keys(st).sort().map(k => n ? st[k] : `${k} = ${st[k]}`).join('\n') + '\n'); return 0; }
    if (!keys.length) { this.eout('sysctl: no variables specified\nTry `sysctl --help\' for more information.\n'); return 1; }
    for (const x0 of keys) {
      const eq = x0.indexOf('='), k = (eq >= 0 ? x0.slice(0, eq) : x0).replace(/\//g, '.'), val = eq >= 0 ? x0.slice(eq + 1) : null;
      if (!(k in st)) { this.eout(`sysctl: cannot stat /proc/sys/${k.replace(/\./g, '/')}: No such file or directory\n`); code = 255; continue; }
      if (val !== null || w) {
        if (val === null) { this.eout(`sysctl: "${k}" must be of the form name=value\n`); code = 255; continue; }
        if (this.user !== 'root') { this.eout(`sysctl: permission denied on key "${k}"\n`); code = 255; continue; }
        if (/^kernel\.os/.test(k)) { this.eout(`sysctl: permission denied on key "${k}"\n`); code = 255; continue; }
        st[k] = val; this.out(n ? val + '\n' : `${k} = ${val}\n`); continue;
      }
      this.out(n ? st[k] + '\n' : `${k} = ${st[k]}\n`);
    }
    return code;
  };

  /* capabilities: names in bit order as libcap 2.66 prints them */
  const CAPS = 'chown dac_override dac_read_search fowner fsetid kill setgid setuid setpcap linux_immutable net_bind_service net_broadcast net_admin net_raw ipc_lock ipc_owner sys_module sys_rawio sys_chroot sys_ptrace sys_pacct sys_admin sys_boot sys_nice sys_resource sys_time sys_tty_config mknod lease audit_write audit_control setfcap mac_override mac_admin syslog wake_alarm block_suspend audit_read perfmon bpf checkpoint_restore'.split(' ');
  C.capsh = function (a) {
    const d = a.find(x => x.startsWith('--decode='));
    if (d) { const hex = d.slice(9).replace(/^0x/, ''); let v = BigInt('0x' + (hex || '0')); const names = []; CAPS.forEach((c, i) => { if ((v >> BigInt(i)) & 1n) names.push('cap_' + c); }); this.out(`0x${hex.padStart(16, '0')}=${names.join(',')}\n`); return 0; }
    if (a.includes('--print')) { const root = this.user === 'root', all = CAPS.map(c => 'cap_' + c).join(','); this.out(`Current: ${root ? '=ep' : '='}\nBounding set =${all}\nAmbient set =\nCurrent IAB: \nSecurebits: 00/0x0/1'b0 (no-new-privs=0)\n secure-noroot: no (unlocked)\n secure-no-suid-fixup: no (unlocked)\n secure-keep-caps: no (unlocked)\n secure-no-ambient-raise: no (unlocked)\nuid=${root ? 0 : 1000}(${this.user}) euid=${root ? 0 : 1000}(${this.user})\ngid=${root ? 0 : 1000}(${root ? 'root' : USER})\ngroups=${root ? '0(root)' : '27(sudo),1000(learner)'}\nGuessed mode: HYBRID (4)\n`); return 0; }
    this.eout('capsh: in the practice shell use capsh --decode=HEX or capsh --print\n'); return 1;
  };
  World.prototype.fcaps = function () { if (!this.fcapState) this.fcapState = { '/usr/bin/ping': 'cap_net_raw=ep' }; return this.fcapState; };
  C.getcap = function (a) {
    const [f, rest] = opts(a); const st = this.fcaps();
    if (f.r) { const base = this.abs(rest[0] || '.'); Object.keys(st).sort().filter(k => k.startsWith(base === '/' ? '/' : base + '/')).forEach(k => this.out(`${k} ${st[k]}\n`)); return 0; }
    for (const t of rest) { const p = this.abs(t); if (!this.node(p)) { this.eout(`Failed to get capabilities of file '${t}' (No such file or directory)\n`); continue; } if (st[p]) this.out(`${t} ${st[p]}\n`); }
    return 0;
  };
  C.setcap = function (a) {
    if (this.user !== 'root') { this.eout('unable to set CAP_SETFCAP effective capability: Operation not permitted\n'); return 1; }
    const rm = a[0] === '-r', spec = rm ? null : a[0], t = rm ? a[1] : a[1];
    if (!t || !this.node(this.abs(t))) { this.eout(`Failed to set capabilities on file '${t}' (No such file or directory)\n`); return 1; }
    const st = this.fcaps(), p = this.abs(t);
    if (rm) { delete st[p]; return 0; }
    const m = /^((?:cap_[a-z_]+,?)+)[=+-]+([eip]*)$/.exec(spec || '');
    if (!m) { this.eout(`fatal error: Invalid argument\nusage: setcap [-h] [-q] [-v] [-n <rootid>] (-r|-|<caps>) <filename> [ ... (-r|-|<capsN>) <filenameN> ]\n`); return 1; }
    st[p] = `${m[1]}=${m[2]}`; return 0;
  };
  C.lsblk = function (a) {
    const st = this.disks(), full = a.includes('-f') || a.includes('--fs'), names = a.filter(x => !x.startsWith('-')).map(x => x.replace(/^\/dev\//, ''));
    const mnt = p => (st.mounts.find(m => m.dev === p.name) || {}).dir || (st.swaps.some(x => x.dev === p) ? '[SWAP]' : '');
    const devs = st.devs.filter(d => !names.length || names.includes(d.name));
    const rows = [];
    const lvsOn = (x, pre) => st.lvm.lvs.filter(lv => lv.pvs.includes(x.name)).forEach((lv, i, A) => rows.push([pre + (i === A.length - 1 ? '└─' : '├─') + lv.vg + '-' + lv.lv, lv, 'lvm']));
    devs.forEach(d => { rows.push([d.name, d, 'disk']); lvsOn(d, ''); d.parts.forEach((p, i) => { rows.push([(i === d.parts.length - 1 ? '└─' : '├─') + p.name, p, 'part']); lvsOn(p, i === d.parts.length - 1 ? '  ' : '│ '); }); });
    if (!rows.length) { this.eout(`lsblk: ${names[0]}: not a block device\n`); return 32; }
    const w = Math.max(4, ...rows.map(r => r[0].length));
    if (full) {
      const fsr = rows.map(([n, x]) => { const P = st.lvm.pvs[x.name]; const fs = P ? { type: 'LVM2_member', label: '', uuid: P.uuid, ver: 'LVM2 001' } : x.fs; const m = mnt(x); const mm = m && m !== '[SWAP]'; const avail = fs && mm ? humanBin(fs.avail * 1024) : ''; const pct = fs && mm ? Math.ceil(fs.used * 100 / (fs.used + fs.avail)) + '%' : ''; return [n, fs ? fs.type : '', fs ? (fs.ver ? fs.ver : fs.type === 'swap' ? '1' : fs.type === 'ext4' ? '1.0' : fs.type === 'vfat' ? 'FAT32' : fs.type === 'xfs' ? '' : '') : '', fs ? fs.label : '', fs ? fs.uuid : '', avail, pct, m]; });
      const head = ['NAME', 'FSTYPE', 'FSVER', 'LABEL', 'UUID', 'FSAVAIL', 'FSUSE%', 'MOUNTPOINTS'], all = [head].concat(fsr), ww = head.map((_, i) => Math.max(...all.map(r => r[i].length)));
      this.out(all.map(r => r.map((x, i) => i === 7 ? x : i === 5 || i === 6 ? x.padStart(ww[i]) : x.padEnd(ww[i])).join(' ').replace(/\s+$/, '')).join('\n') + '\n');
      return 0;
    }
    this.out(`${'NAME'.padEnd(w)} MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS\n` + rows.map(([n, x, t]) => `${n.padEnd(w)} ${x.mm.padStart(5)}  ${(x.rm !== undefined ? x.rm : t === 'lvm' ? 0 : st.devs.find(d => d.parts.includes(x)).rm)} ${humanBin(x.size).padStart(5)}  0 ${t.padEnd(4)} ${mnt(x)}`.replace(/\s+$/, '')).join('\n') + '\n');
    return 0;
  };
  C.blkid = function (a) {
    const st = this.disks(), names = a.filter(x => !x.startsWith('-')).map(x => { const q = this.partOf(x); return q ? q.name : x.replace(/^\/dev\//, ''); });
    if (this.user !== 'root' && !names.length) { /* blkid as a user prints from its cache, which may be empty */ }
    let any = false;
    st.devs.concat([{ parts: st.lvm.lvs, label: null }]).forEach(d => d.parts.forEach(p => { if ((!names.length || names.includes(p.name)) && p.fs) { any = true; this.out(`/dev/${p.name}: ${p.fs.label ? `LABEL="${p.fs.label}" ` : ''}UUID="${p.fs.uuid}" ${p.fs.type === 'vfat' ? 'BLOCK_SIZE="512" ' : 'BLOCK_SIZE="4096" '}TYPE="${p.fs.type}"${d.label === 'gpt' && p.pname ? ` PARTLABEL="${p.pname}"` : ''}${d.label ? ` PARTUUID="${d.label === 'gpt' ? (d.name === 'sda' ? '7c9e4b1d' : 'e3a95f20') + '-0' + p.name.slice(-1) + '2a-4f3e-8d6c-5b1a9e7f3c2' + p.name.slice(-1) : 'a1b2c3d4-0' + p.name.slice(-1)}"` : ''}\n`); } }));
    Object.keys(st.lvm.pvs).forEach(n => { if (!names.length || names.includes(n)) { any = true; this.out(`/dev/${n}: UUID="${st.lvm.pvs[n].uuid}" TYPE="LVM2_member"\n`); } });
    return any ? 0 : 2;
  };
  World.prototype.needRootDisk = function (cmd) { if (this.user === 'root') return false; this.eout(cmd === 'mount' || cmd === 'umount' ? '' : `${cmd}: Permission denied\n`); return true; };
  C.parted = function (a) {
    let args = a.filter(x => x !== '-s' && x !== '--script'), script = a.includes('-s') || a.includes('--script');
    const dev = args[0], d = this.partOf(dev);
    if (!d || !d.parts) { this.eout(`Error: Could not stat device ${dev || ''} - No such file or directory.\n`); return 1; }
    if (this.user !== 'root') { this.eout(`Error: Error opening ${dev}: Permission denied\n`); return 1; }
    args = args.slice(1);
    if (!args.length) { this.eout('parted would now open its own prompt, which the practice shell cannot do. Give the commands on the line instead, for example: sudo parted -s ' + dev + ' print\n'); return 1; }
    const gb = b => (b / 1e9 >= 1 ? (Math.round(b / 1e8) / 10) + 'GB' : Math.round(b / 1e3) + 'kB');
    const pos = (x, size) => { const m = /^([\d.]+)(%|MiB|GiB|MB|GB|s)?$/.exec(x); if (!m) return NaN; const v = +m[1]; return m[2] === '%' ? Math.min(size, Math.round(size * v / 100 / MiB) * MiB) : m[2] === 'GiB' ? v * GiB : m[2] === 'GB' ? v * 1e9 : m[2] === 's' ? v * 512 : v * MiB; };
    while (args.length) {
      const c = args.shift();
      if (c === 'mklabel') { const t = args.shift(); if (!['gpt', 'msdos'].includes(t)) { this.eout(`Error: Invalid disk label type ${t}.\n`); return 1; } if (d.parts.some(p => this.disks().mounts.some(m => m.dev === p.name))) { this.eout(`Error: Partition(s) on ${dev} are being used.\n`); return 1; } d.label = t; d.parts = []; }
      else if (c === 'mkpart') {
        if (!d.label) { this.eout(`Error: ${dev}: unrecognised disk label\n`); return 1; }
        let pname = ''; if (d.label === 'gpt') pname = args.shift(); else args.shift();
        if (/^(ext4|xfs|fat32|linux-swap|btrfs)$/.test(args[0])) args.shift();
        const st0 = pos(args.shift(), d.size), enArg = args.shift(); let en = pos(enArg, d.size); if (enArg === '100%' && d.label === 'gpt') en = d.size - MiB;
        if (isNaN(st0) || isNaN(en) || en <= st0) { this.eout('Error: Invalid start or end of the partition.\n'); return 1; }
        if (d.parts.some(p => st0 < p.start + p.size && en > p.start)) { this.eout("Error: You requested a partition from the given range, but it overlaps another partition.\n"); return 1; }
        const k = d.parts.length + 1, base = { sda: 0, sdb: 16, sdc: 32 }[d.name] || 48;
        d.parts.push({ name: d.name + k, mm: `8:${base + k}`, size: en - st0, start: st0, pname, fs: null });
        this.mk('/dev/' + d.name + k, 'b', 0o660, 'root', '').group = 'disk';
      }
      else if (c === 'print') {
        if (!d.label) { this.eout(`Error: ${dev}: unrecognised disk label\n`); this.out(`Model: ${d.model}\nDisk ${dev}: ${gb(d.size)}\nSector size (logical/physical): 512B/512B\nPartition Table: unknown\nDisk Flags: \n`); return 1; }
        this.out(`Model: ${d.model}\nDisk ${dev}: ${gb(d.size)}\nSector size (logical/physical): 512B/512B\nPartition Table: ${d.label}\nDisk Flags: \n\nNumber  Start   End     Size    ${d.label === 'gpt' ? 'File system  Name  Flags' : 'Type     File system  Flags'}\n` + d.parts.map((p, i) => ` ${i + 1}      ${gb(p.start).padEnd(7)} ${gb(p.start + p.size).padEnd(7)} ${gb(p.size).padEnd(7)} ${d.label === 'gpt' ? `${(p.fs ? p.fs.type : '').padEnd(12)} ${p.pname}` : `primary  ${(p.fs ? (p.fs.type === 'vfat' ? 'fat32' : p.fs.type) : '').padEnd(12)} lba`}`).join('\n') + '\n\n');
      }
      else if (c === 'rm') { const n = +args.shift(); d.parts.splice(n - 1, 1); }
      else { this.eout(`Error: the practice parted knows mklabel, mkpart, print and rm, not ${c}.\n`); return 1; }
    }
    return 0;
  };
  const sbList = n => { const L = [32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208, 4096000, 7962624, 11239424, 20480000, 23887872].filter(b => b < n), out = []; for (let i = 0; i < L.length; i += 9) out.push(L.slice(i, i + 9).join(', ')); return out.join(', \n\t'); };
  const jBlocks = n => n < 32768 ? 1024 : n < 262144 ? 4096 : n < 524288 ? 8192 : n < 4194304 ? 16384 : n < 8388608 ? 32768 : n < 16777216 ? 65536 : n < 33554432 ? 131072 : 262144;
  C['mkfs.ext4'] = C['mkfs.xfs'] = C['mkfs.vfat'] = C.mkfs = function (a, input) {
    let type = { 'mkfs.ext4': 'ext4', 'mkfs.xfs': 'xfs', 'mkfs.vfat': 'vfat' }[this.cmdNameReal] || 'ext4', label = '', force = false; const rest = [];
    for (let i = 0; i < a.length; i++) { if (a[i] === '-t') type = a[++i]; else if (a[i] === '-L' || a[i] === '-n') label = a[++i]; else if (a[i] === '-F' || a[i] === '-f') force = true; else if (!a[i].startsWith('-')) rest.push(a[i]); }
    const dev = rest[0], p = this.partOf(dev), prog = type === 'ext4' ? 'mke2fs' : type === 'xfs' ? 'mkfs.xfs' : 'mkfs.fat';
    if (!p) { this.eout(`${prog === 'mke2fs' ? 'mke2fs 1.47.0 (5-Feb-2023)\n' : ''}The file ${dev} does not exist and no size was specified.\n`); return 1; }
    if (this.user !== 'root') { this.eout(`${prog === 'mke2fs' ? 'mke2fs 1.47.0 (5-Feb-2023)\nmkfs.ext4: ' : prog + ': '}Permission denied while trying to determine filesystem size\n`); return 1; }
    if (p.parts) { this.eout(`${prog}: ${dev} is a whole disk. The practice shell formats partitions only, so create one with parted first.\n`); return 1; }
    if (this.disks().mounts.some(m => m.dev === p.name)) { this.eout(`${prog === 'mke2fs' ? 'mke2fs 1.47.0 (5-Feb-2023)\n' : ''}${dev} is mounted; will not make a filesystem here!\n`); return 1; }
    if (p.fs && !force && type === 'ext4') { this.out(`mke2fs 1.47.0 (5-Feb-2023)\n${dev} contains a ${p.fs.type} file system${p.fs.label ? ` labelled '${p.fs.label}'` : ''}\nProceed anyway? (y,N) `); if (!/^\s*y/i.test(input || '')) { this.out('\n'); return 1; } this.out('y\n'); }
    if (a.includes('-q')) { const o = this.out; this.out = () => {}; try { return C.mkfs.call(this, a.filter(x => x !== '-q'), 'y'); } finally { this.out = o; } }
    const blocks4k = Math.floor(p.size / 4096), k = blocks4k * 4;
    const uuid = type === 'vfat' ? newUuid(this, dev).slice(0, 4).toUpperCase() + '-' + newUuid(this, dev + 'x').slice(0, 4).toUpperCase() : newUuid(this, dev);
    const real20 = blocks4k === 5242368;
    if (type === 'ext4') {
      const inodes = real20 ? 1310720 : Math.floor(blocks4k / 4 / 8192) * 8192 || 8192;
      this.out(`${p.fs ? '' : 'mke2fs 1.47.0 (5-Feb-2023)\n'}Creating filesystem with ${blocks4k} 4k blocks and ${inodes} inodes\nFilesystem UUID: ${uuid}\nSuperblock backups stored on blocks: \n\t${sbList(blocks4k)}\n\nAllocating group tables: done                            \nWriting inode tables: done                            \nCreating journal (${jBlocks(blocks4k)} blocks): done\nWriting superblocks and filesystem accounting information: done\n\n`);
      p.fs = { type: 'ext4', uuid, label, blocks: real20 ? 20464208 : Math.round(k * 0.976), used: 24, avail: real20 ? 19399328 : Math.round(k * 0.925), inodes, iused: 11 };
      p.fs.tree = { type: 'd', name: '/', mode: 0o755, owner: 'root', group: 'root', mtime: this.now(), kids: { 'lost+found': { type: 'd', name: 'lost+found', mode: 0o700, owner: 'root', group: 'root', mtime: this.clock, kids: {} } } };
    } else if (type === 'xfs') {
      this.out(`meta-data=${dev}              isize=512    agcount=4, agsize=${Math.ceil(blocks4k / 4)} blks\n         =                       sectsz=512   attr=2, projid32bit=1\n         =                       crc=1        finobt=1, sparse=1, rmapbt=1\n         =                       reflink=1    bigtime=1 inobtcount=1 nrext64=0\ndata     =                       bsize=4096   blocks=${blocks4k}, imaxpct=25\n         =                       sunit=0      swidth=0 blks\nnaming   =version 2              bsize=4096   ascii-ci=0, ftype=1\nlog      =internal log           bsize=4096   blocks=16384, version=2\n         =                       sectsz=512   sunit=0 blks, lazy-count=1\nrealtime =none                   extsz=4096   blocks=0, rtextents=0\n`);
      p.fs = { type: 'xfs', uuid, label, blocks: Math.round(k * 0.995), used: Math.round(k * 0.0075), avail: Math.round(k * 0.9875), inodes: Math.round(k / 2), iused: 3, tree: { type: 'd', name: '/', mode: 0o755, owner: 'root', group: 'root', mtime: this.now(), kids: {} } };
    } else {
      this.out('mkfs.fat 4.2 (2021-01-31)\n');
      p.fs = { type: 'vfat', uuid, label: label.toUpperCase(), blocks: Math.round(k * 0.998), used: 4, avail: Math.round(k * 0.998) - 4, inodes: 0, iused: 0, tree: { type: 'd', name: '/', mode: 0o755, owner: 'root', group: 'root', mtime: this.now(), kids: {} } };
    }
    return 0;
  };
  World.prototype.doMount = function (devArg, dir, opts) {
    const st = this.disks(), p = this.partOf(devArg), d = this.abs(dir), dn = this.node(d);
    if (!dn || dn.type !== 'd') { this.eout(`mount: ${d}: mount point does not exist.\n`); return 32; }
    if (!p) { this.eout(/^(UUID|LABEL)=/.test(devArg) ? `mount: ${d}: can't find ${devArg}.\n` : `mount: ${d}: special device ${devArg} does not exist.\n`); return 32; }
    if (!p.fs || p.parts) { this.eout(`mount: ${d}: wrong fs type, bad option, bad superblock on /dev/${p.name}, missing codepage or helper program, or other error.\n       dmesg(1) may have more information after failed mount system call.\n`); return 32; }
    const had = st.mounts.find(m => m.dev === p.name); if (had) { this.eout(`mount: ${d}: /dev/${p.name} already mounted on ${had.dir}.\n`); return 32; }
    if (st.mounts.some(m => m.dir === d)) { /* stacking a second mount on the same folder is allowed, the newest hides the older */ }
    const keep = dn.kids; dn.kids = p.fs.tree.kids; const saved = { mode: dn.mode, owner: dn.owner, group: dn.group };
    dn.mode = p.fs.tree.mode; dn.owner = p.fs.tree.owner; dn.group = p.fs.tree.group;
    st.mounts.push({ dev: p.name, dir: d, opts: opts || (p.fs.type === 'vfat' ? 'rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=ascii,shortname=mixed,utf8,errors=remount-ro' : 'rw,relatime'), under: keep, saved });
    this.sdLog('', 'kernel', p.fs.type === 'ext4' ? `EXT4-fs (${p.name}): mounted filesystem ${p.fs.uuid} r/w with ordered data mode. Quota mode: none.` : p.fs.type === 'xfs' ? `XFS (${p.name}): Mounting V5 Filesystem ${p.fs.uuid}` : `FAT-fs (${p.name}): Volume was not properly unmounted. Some data may be corrupt. Please run fsck.`);
    return 0;
  };
  C.mount = function (a) {
    const st = this.disks();
    let type = '', opts = ''; const rest = [];
    for (let i = 0; i < a.length; i++) { if (a[i] === '-t') type = a[++i]; else if (a[i] === '-o') opts = a[++i]; else if (a[i] === '-a') rest.push('-a'); else if (a[i] === '-v') continue; else rest.push(a[i]); }
    if (!rest.length || (type && !rest.length)) {
      this.out(this.mountTable().filter(r => !type || r.type === type).map(r => `${r.src} on ${r.dir} type ${r.type} (${r.opts})`).join('\n') + '\n'); return 0;
    }
    if (this.user !== 'root') { const d = rest[rest.length - 1]; this.eout(`mount: ${d === '-a' ? '' : this.abs(d) + ': '}must be superuser to use mount.\n`); return 1; }
    const fstab = () => (this.node('/etc/fstab').data || '').split('\n').filter(l => l.trim() && !l.trim().startsWith('#')).map(l => l.trim().split(/\s+/));
    if (rest[0] === '-a') {
      let code = 0;
      fstab().forEach(f => {
        const [src, dir, t, o] = f; if (t === 'swap' || (o || '').split(',').includes('noauto') || dir === '/') return;
        if (st.mounts.some(m => m.dir === dir)) return;
        const p = this.partOf(src);
        if (!p && (o || '').split(',').includes('nofail')) return;
        if (this.doMount(src, dir, (o || 'defaults') === 'defaults' ? null : 'rw,relatime,' + o.split(',').filter(x => x !== 'defaults' && x !== 'nofail').join(','))) code = 32;
      });
      return code;
    }
    if (rest.length === 1) {
      const row = fstab().find(f => f[1] === this.abs(rest[0]) || f[0] === rest[0] || f[0] === 'UUID=' + rest[0]);
      if (!row) { this.eout(`mount: ${rest[0]}: can't find in /etc/fstab.\n`); return 1; }
      return this.doMount(row[0], row[1]);
    }
    return this.doMount(rest[0], rest[1], opts ? 'rw,relatime,' + opts.split(',').filter(x => x !== 'rw').join(',') : null);
  };
  C.umount = function (a) {
    const st = this.disks(), x = a.filter(y => !y.startsWith('-'))[0];
    if (!x) { this.eout('Usage:\n umount [-hV]\n umount -a [options]\n umount [options] <source> | <directory>\n'); return 1; }
    const d = this.abs(x), dev = x.replace(/^\/dev\//, '');
    const k = st.mounts.map((m, i) => [m, i]).reverse().find(([m]) => m.dir === d || m.dev === dev);
    if (this.user !== 'root') { this.eout(`umount: ${d}: must be superuser to unmount.\n`); return 1; }
    if (!k) { this.eout(`umount: ${d}: not mounted.\n`); return 32; }
    const [m, i] = k;
    if (m.dir === '/') { this.eout('umount: /: target is busy.\n'); return 32; }
    if (this.cwd === m.dir || this.cwd.startsWith(m.dir + '/')) { this.eout(`umount: ${m.dir}: target is busy.\n`); return 32; }
    const dn = this.node(m.dir), p = this.partOf(m.dev);
    p.fs.tree.kids = dn.kids; p.fs.tree.mode = dn.mode; p.fs.tree.owner = dn.owner; p.fs.tree.group = dn.group;
    dn.kids = m.under; Object.assign(dn, m.saved);
    st.mounts.splice(i, 1);
    return 0;
  };
  C.findmnt = function (a) {
    const rows = this.mountTable();
    if (a.includes('--verify')) {
      const lines = (this.node('/etc/fstab').data || '').split('\n').filter(l => l.trim() && !l.trim().startsWith('#')).map(l => l.trim().split(/\s+/));
      let errs = 0, warns = 0, out = '';
      lines.forEach(f => {
        const [src, dir, t, o, dump, pass] = f, msgs = [];
        if (f.length < 4) { msgs.push(['E', 'not enough fields']); }
        else {
          if (t !== 'swap' && !this.node(dir)) msgs.push(['E', 'unreachable on boot required target: No such file or directory']);
          if (!this.partOf(src)) { if (/^(UUID|LABEL|PARTUUID|PARTLABEL)=/.test(src)) msgs.push(['E', `unreachable on boot required source: ${src}`]); else msgs.push(['W', `unreachable source: ${src}: No such file or directory`], ['W', 'cannot detect on-disk filesystem type (No such file or directory)']); }
          else { const p = this.partOf(src); if (p.fs && t !== 'auto' && p.fs.type !== t) msgs.push(['W', `${t} does not match with on-disk ${p.fs.type}`]); }
          if (pass !== undefined && !/^[0-2]$/.test(pass)) msgs.push(['W', `fs_passno ${pass} is not 0, 1 or 2`]);
        }
        if (msgs.length) { out += dir + '\n' + msgs.map(([k, m]) => `   [${k}] ${m}`).join('\n') + '\n'; msgs.forEach(([k]) => k === 'E' ? errs++ : warns++); }
      });
      this.out(out + (errs || warns ? `\n0 parse errors, ${errs} error${errs === 1 ? '' : 's'}, ${warns} warning${warns === 1 ? '' : 's'}\n` : 'Success, no errors or warnings detected\n'));
      return errs ? 1 : 0;
    }
    const t = a.filter(x => !x.startsWith('-'))[0];
    const show = t ? rows.filter(r => r.dir === this.abs(t) || r.src === t) : rows;
    if (!show.length) return 1;
    const w = [Math.max(6, ...show.map(r => r.dir.length)), Math.max(6, ...show.map(r => r.src.length)), Math.max(6, ...show.map(r => r.type.length))];
    this.out(`${'TARGET'.padEnd(w[0])} ${'SOURCE'.padEnd(w[1])} ${'FSTYPE'.padEnd(w[2])} OPTIONS\n` + show.map(r => `${r.dir.padEnd(w[0])} ${r.src.padEnd(w[1])} ${r.type.padEnd(w[2])} ${r.opts}`).join('\n') + '\n');
    return 0;
  };
  C.fsck = C.e2fsck = function (a) {
    const dev = a.filter(x => !x.startsWith('-'))[0], p = this.partOf(dev);
    const head = this.cmdNameReal === 'e2fsck' ? 'e2fsck 1.47.0 (5-Feb-2023)\n' : 'fsck from util-linux 2.39.3\ne2fsck 1.47.0 (5-Feb-2023)\n';
    if (!p) { this.out('fsck from util-linux 2.39.3\n'); this.eout(`fsck.ext2: No such file or directory while trying to open ${dev}\n`); return 8; }
    if (this.user !== 'root') { this.out(head); this.eout(`fsck.ext4: Permission denied while trying to open ${dev}\nYou must have r/w access to the filesystem or be root\n`); return 8; }
    if (this.disks().mounts.some(m => m.dev === p.name)) { this.out(head + `${dev} is mounted.\ne2fsck: Cannot continue, aborting.\n\n`); return 8; }
    if (!p.fs) { this.out(head); this.eout(`ext2fs_open2: Bad magic number in super-block\nfsck.ext2: Superblock invalid, trying backup blocks....\nfsck.ext2: Bad magic number in super-block while trying to open ${dev}\n`); return 8; }
    if (p.fs.type === 'vfat') { this.out(`fsck from util-linux 2.39.3\nfsck.fat 4.2 (2021-01-31)\n${dev}: 3 files, 540/7813628 clusters\n`); return 0; }
    this.out(head + `${p.fs.label || dev}: clean, ${p.fs.iused}/${p.fs.inodes} files, ${p.fs.type === 'ext4' && p.fs.inodes === 1310720 ? 126322 : Math.round(p.fs.used / 4) + 120000}/${Math.floor(p.size / 4096)} blocks\n`);
    return 0;
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
        const typ = n.type === 'd' ? 'directory' : n.type === 'l' ? 'symbolic link' : n.type === 'p' ? 'fifo' : n.type === 'c' ? 'character special file' : this.size(n) ? 'regular file' : 'regular empty file';
        const map = { i: String(this.ino(n)), h: String(this.links(n)), a: n.mode.toString(8), A: modeStr(n), n: t, U: n.owner, G: n.group, u: String(this.pwRow(n.owner) ? this.pwRow(n.owner)[2] : 1000), g: String(this.grRow(n.group) ? this.grRow(n.group)[2] : 1000), s: String(this.size(n)), F: typ, '%': '%' };
        this.out(String(f.c).replace(/%(.)/g, (m, k) => map[k] ?? m) + '\n');
        return;
      }
      const ty = n.type === 'd' ? 'directory' : n.type === 'l' ? 'symbolic link' : n.type === 'p' ? 'fifo' : n.type === 'c' ? 'character special file' : this.size(n) ? 'regular file' : 'regular empty file';
      const dt = new Date(n.mtime).toISOString().replace('T', ' ').replace(/\.\d+Z/, '.000000000 +0000');
      this.out(`  File: ${t}${n.type === 'l' ? ' -> ' + n.target : ''}\n  Size: ${this.size(n)}\t\tBlocks: ${n.type === 'd' ? 8 : this.size(n) ? 8 : 0}\tIO Block: 4096   ${ty}\nDevice: ${n.proc ? '0,22' : '8,1'}\tInode: ${String(this.ino(n)).padEnd(11)} Links: ${this.links(n)}\nAccess: (${n.mode.toString(8).padStart(4, '0')}/${modeStr(n)})  Uid: (${pad(this.pwRow(n.owner) ? this.pwRow(n.owner)[2] : 1000, 5)}/${pad(n.owner, 8)})   Gid: (${pad(this.grRow(n.group) ? this.grRow(n.group)[2] : 1000, 5)}/${pad(n.group, 8)})\nAccess: ${dt}\nModify: ${dt}\nChange: ${dt}\n Birth: ${dt}\n`);
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
    if (this.mountOf(this.abs(tgt)) !== this.mountOf(to)) { this.eout(`ln: failed to create hard link '${link}' => '${tgt}': Invalid cross-device link\n`); return 1; }
    if (this.user !== 'root' && src.owner !== this.user && !(this.can(src, 'r') && this.can(src, 'w'))) { this.eout(`ln: failed to create hard link '${link}' => '${tgt}': Operation not permitted\n`); return 1; }
    this.node(dirName(to)).kids[baseName(to)] = src;   /* the same node under a second name, just like a hard link */
  };
  C.readlink = function (a) { const [f, rest] = opts(a); const n = this.node(this.abs(rest[0]), false); if (f.f || f.e || f.m) { const r = this.canon(this.abs(rest[0])); if (r === null || (f.e && !this.node(r))) return 1; this.out(r + '\n'); return 0; } if (!n || n.type !== 'l') return 1; this.out(n.target + '\n'); };
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
      if (o === '-inum') { const v = need(o); return c => cmpNum(v, self.ino(c.n)); }
      if (o === '-samefile') { const v = need(o), r = self.node(self.abs(v)); if (!r) throw new Error(`‘${v}’: No such file or directory`); return c => c.n === r; }
      if (o === '-links') { const v = need(o); return c => cmpNum(v, self.links(c.n)); }
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
    const so = flat.match(/--sort[= ](-?)([%\w]+)/);
    if (so) { const key = { '%cpu': p => p.cpu || 0, pcpu: p => p.cpu || 0, '%mem': p => p.pid % 700, rss: p => p.pid % 700, pid: p => p.pid }[so[2]] || (p => p.pid); rows = rows.slice().sort((x, y) => (so[1] ? key(y) - key(x) : key(x) - key(y)) || x.pid - y.pid); }
    const tty = p => p.ppid === 2001 || p.pid === 2001 ? 'pts/0' : '?';
    const t0 = p => when(p.start || T0 - 3 * 86400000).slice(7);
    const oi = a.findIndex(x => x === '-o' || x === '-eo' || x === 'o');
    if (oi >= 0) {
      const cols = a[oi + 1].split(',');
      const H = { vsz: ['VSZ', 6], rss: ['RSS', 5], pid: ['PID', 7], lwp: ['LWP', 7], nlwp: ['NLWP', 4], ppid: ['PPID', 7], user: ['USER', -8], stat: ['STAT', -4], ni: ['NI', 3], comm: ['COMMAND', -15], cmd: ['CMD', 0], args: ['COMMAND', 0], '%cpu': ['%CPU', 4], '%mem': ['%MEM', 4], tty: ['TT', -8], etime: ['ELAPSED', 11] };
      const val = (p, c) => ({ vsz: p.pid === 1 ? 167700 : 8000 + p.pid % 900 * 7, rss: p.pid === 1 ? 13020 : 3000 + p.pid % 700 * 3, pid: p.pid, lwp: p.pid, nlwp: 1, ppid: p.ppid, user: p.user, stat: p.stat + (p.pid === 2001 ? 's' : ''), ni: p.ni || 0, comm: comm(p), cmd: p.cmd, args: p.cmd, '%cpu': (p.cpu || 0).toFixed(1), '%mem': '0.1', tty: tty(p), etime: '00:' + pad(Math.max(0, Math.round((this.clock - (p.start || T0)) / 1000)) % 60, 2).replace(' ', '0') })[c];
      const line = f => cols.map((c, k) => { const [, w] = H[c] || [c.toUpperCase(), 8]; const s = String(f(c)); return k === cols.length - 1 && w <= 0 ? s : w < 0 ? pad(s, -w, true) : pad(s, w); }).join(' ');
      this.out(line(c => (H[c] || [c.toUpperCase()])[0]).replace(/\s+$/, '') + '\n' + rows.map(p => line(c => val(p, c))).join('\n') + '\n');
      return 0;
    }
    if (/u/.test(flat) && !/-u/.test(flat)) { this.out('USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n' + rows.map(p => `${pad(p.user, 8, true)} ${pad(p.pid, 7)} ${pad((p.cpu || 0).toFixed(1), 4)}  0.1  ${pad(p.pid === 1 ? 167700 : 8000 + p.pid % 900 * 7, 6)} ${pad(p.pid === 1 ? 13020 : 3000 + p.pid % 700 * 3, 5)} ${pad(tty(p), 8, true)} ${pad(p.stat + (p.pid === 2001 || p.pid === 1 ? 's' : ''), 4, true)} ${pad(t0(p), 5)}   0:00 ${p.cmd}`).join('\n') + '\n'); return 0; }
    if (/-ef|-f/.test(flat)) { this.out('UID          PID    PPID  C STIME TTY          TIME CMD\n' + rows.map(p => `${pad(p.user, 8, true)} ${pad(p.pid, 7)} ${pad(p.ppid, 7)}  0 ${t0(p)} ${pad(tty(p), 8, true)} 00:00:00 ${p.cmd}`).join('\n') + '\n'); return 0; }
    if (/(^|\s)-L\b/.test(flat)) { this.out('    PID     LWP TTY          TIME CMD\n' + rows.map(p => `${pad(p.pid, 7)} ${pad(p.pid, 7)} ${pad(tty(p), 8, true)} 00:00:00 ${comm(p)}`).join('\n') + '\n'); return 0; }
    this.out('    PID TTY          TIME CMD\n' + rows.map(p => `${pad(p.pid, 7)} ${pad(tty(p), 8, true)} 00:00:00 ${comm(p)}`).join('\n') + '\n');
    return 0;
  };
  /* pstree as psmisc 23.7 draws it: children sorted by name, equal leaves merged as N*[name] unless -p */
  C.pstree = function (a) {
    const [f] = opts(a);
    const rows = this.allProcs().map(p => p.me ? Object.assign({}, p, { cmd: 'pstree' }) : p);
    const nm = p => (p.pid === 1 ? 'systemd' : comm(p).replace(/:$/, '')) + (f.p ? `(${p.pid})` : '');
    const kids = pid => rows.filter(p => p.ppid === pid && p.pid !== pid).sort((x, y) => nm(x).localeCompare(nm(y)) || x.pid - y.pid);
    const draw = p => {
      let ch = kids(p.pid).map(k => ({ p: k, lines: draw(k) }));
      if (!f.p) { const out = []; for (const c of ch) { const last = out[out.length - 1]; if (last && last.lines.length === 1 && c.lines.length === 1 && last.lines[0].replace(/^\d+\*\[(.*)\]$/, '$1') === c.lines[0]) { last.n = (last.n || 1) + 1; last.lines = [`${last.n}*[${c.lines[0]}]`]; } else out.push(Object.assign({}, c, { lines: c.lines.slice() })); } ch = out; }
      const me = nm(p);
      if (!ch.length) return [me];
      const ind = ' '.repeat(me.length);
      if (ch.length === 1) return ch[0].lines.map((l, i) => (i ? ind + '   ' : me + '───') + l);
      const res = [];
      ch.forEach((c, i) => c.lines.forEach((l, j) => {
        const first = i === 0 && j === 0, lastc = i === ch.length - 1;
        res.push((first ? me + '─┬─' : ind + (j ? (lastc ? '   ' : ' │ ') : (lastc ? ' └─' : ' ├─'))) + l);
      }));
      return res;
    };
    this.out(draw(rows.find(p => p.pid === 1)).join('\n') + '\n');
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
  /* performance tools of procps and sysstat with steady numbers for a quiet 2 CPU practice server */
  const statHead = w => `Linux 6.8.0-practice (${HOST}) \t${(d => `${pad(d.getUTCMonth() + 1, 2).replace(' ', '0')}/${pad(d.getUTCDate(), 2).replace(' ', '0')}/${String(d.getUTCFullYear()).slice(2)}`)(new Date(w.clock))} \t_x86_64_\t(2 CPU)\n`;
  const hms = ms => new Date(ms).toISOString().slice(11, 19);
  const interval = rest => { const n = rest.filter(x => /^\d+$/.test(x)).map(Number); return { delay: n[0], count: n.length > 1 ? n[1] : n.length ? Infinity : 0 }; };
  C.vmstat = function (a) {
    const [f, rest] = opts(a, 'S');
    const { delay, count } = interval(rest);
    const rows = delay ? Math.min(count, 5) : 1, unit = f.S === 'M' ? 1024 : f.S === 'm' ? 1000 / 1.024 : 1;
    const mem = k => Math.round(k / unit), hogs = Math.min(2, this.procs.filter(p => p.cpu).length);
    let o = 'procs -----------memory---------- ---swap-- -----io---- -system-- -------cpu-------\n r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st gu\n';
    for (let i = 0; i < rows; i++) {
      const v = i === 0 ? [1, 0, 0, 3142212, 315556, 2389412, 0, 0, 12, 34, 180, 320, 2, 1, 97, 0, 0, 0] : [i % 2, 0, 0, 3142212 - 96 * i, 315556, 2389412 + 8 * i, 0, 0, 0, 8 * i, 150 + 7 * i, 290 + 11 * i, 1, 0, 99, 0, 0, 0];
      if (i && hogs) { const us = Math.min(99, Math.round(hogs * 99.7 / 2)); v[0] = hogs; v[10] += 900 * hogs; v[11] += 60 * hogs; v[12] = us; v[13] = 1; v[14] = 99 - us; }
      v[3] = mem(v[3]); v[4] = mem(v[4]); v[5] = mem(v[5]);
      const w = [2, 2, 6, 6, 6, 6, 4, 4, 5, 5, 4, 4, 2, 2, 2, 2, 2, 2];
      o += v.map((x, k) => pad(x, w[k])).join(' ') + '\n';
    }
    if (delay && count > 5) o += '(the practice shell stops after 5 lines. A real vmstat keeps printing until the count is reached or you press Ctrl+C)\n';
    this.out(o); this.clock += (rows - 1) * (delay || 0) * 1000; return 0;
  };
  C.iostat = function (a) {
    const [f, rest] = opts(a);
    const { delay, count } = interval(rest);
    const reps = delay ? Math.min(count, 3) : 1;
    let o = statHead(this) + '\n';
    for (let i = 0; i < reps; i++) {
      const q = i === 0 ? 1 : 0.4;
      if (!f.d) o += `avg-cpu:  %user   %nice %system %iowait  %steal   %idle\n${['%user', 'nice', 'sys', 'wa', 'st'].map((k, j) => pad([2.1 * q, 0, 0.8 * q, 0.3 * q, 0][j].toFixed(2), j ? 8 : 15)).join('')}${pad((100 - 3.2 * q).toFixed(2), 8)}\n\n`;
      if (!f.c) {
        const r = (3.10 * q).toFixed(2), rk = (24.5 * q).toFixed(2), wr = (5.42 * q).toFixed(2), wk = (68.2 * q).toFixed(2);
        o += f.x ? 'Device            r/s     rkB/s   rrqm/s  %rrqm r_await rareq-sz     w/s     wkB/s   wrqm/s  %wrqm w_await wareq-sz     d/s     dkB/s   drqm/s  %drqm d_await dareq-sz     f/s f_await  aqu-sz  %util\n' +
          `sda          ${pad(r, 8)} ${pad(rk, 9)} ${pad('0.04', 8)} ${pad('1.27', 6)} ${pad('0.61', 7)} ${pad('7.90', 8)} ${pad(wr, 7)} ${pad(wk, 9)} ${pad('2.31', 8)} ${pad('29.88', 6)} ${pad('1.92', 7)} ${pad('12.58', 8)} ${pad('0.00', 7)} ${pad('0.00', 9)} ${pad('0.00', 8)} ${pad('0.00', 6)} ${pad('0.00', 7)} ${pad('0.00', 8)} ${pad('0.21', 7)} ${pad('0.85', 7)} ${pad('0.01', 7)} ${pad((0.62 * q).toFixed(2), 6)}\n\n`
          : 'Device             tps    kB_read/s    kB_wrtn/s    kB_dscd/s    kB_read    kB_wrtn    kB_dscd\n' +
          `sda          ${pad((8.52 * q).toFixed(2), 9)} ${pad(rk, 12)} ${pad(wk, 12)} ${pad('0.00', 12)} ${pad(i ? Math.round(24.5 * q * delay) : 5694213, 10)} ${pad(i ? Math.round(68.2 * q * delay) : 15852340, 10)} ${pad(0, 10)}\n\n`;
      }
    }
    if (delay && count > 3) o += '(the practice shell stops after 3 reports)\n';
    this.out(o); this.clock += (reps - 1) * (delay || 0) * 1000; return 0;
  };
  C.mpstat = function (a) {
    const [f, rest] = opts(a, 'P');
    const { delay, count } = interval(rest);
    const cpus = f.P === 'ALL' ? ['all', '0', '1'] : f.P !== undefined && f.P !== true ? ['all', ...String(f.P).split(',')].filter((x, i, s) => s.indexOf(x) === i && (x === 'all' || x === '0' || x === '1')) : ['all'];
    const head = t => `${t}     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle\n`;
    const hogs = Math.min(2, this.procs.filter(p => p.cpu).length);
    const line = (t, c, q) => {
      const busy = q < 1 && hogs && (c === '0' || (c === '1' && hogs > 1) || c === 'all');
      const u = busy ? (c === 'all' ? hogs * 49.85 : 99.7) : { all: 2.1, 0: 3.4, 1: 0.8 }[c] * q, s = busy ? (c === 'all' ? 0.15 * hogs + (hogs > 1 ? 0 : 0.1) : 0.3) : { all: 0.8, 0: 1.1, 1: 0.5 }[c] * q, rest = busy ? 0 : 0.4 * q;
      return `${t}     ${pad(c, 3)} ${[u, 0, s, busy ? 0 : 0.3 * q, 0, busy ? 0 : 0.1 * q, 0, 0, 0].map(x => pad(x.toFixed(2), 7)).join(' ')} ${pad(Math.max(0, 100 - u - s - rest).toFixed(2), 7)}\n`;
    };
    let o = statHead(this) + '\n';
    if (!delay) { const t = hms(this.clock); o += head(t) + cpus.map(c => line(t, c, 1)).join(''); }
    else {
      const reps = Math.min(count, 3);
      for (let i = 1; i <= reps; i++) { const t = hms(this.clock + i * delay * 1000); o += head(t) + cpus.map(c => line(t, c, 0.4)).join('') + '\n'; }
      o += head('Average:') .replace('Average:     ', 'Average:     ') + cpus.map(c => line('Average:', c, 0.4)).join('');
      this.clock += reps * delay * 1000;
    }
    this.out(o); return 0;
  };
  C.pidstat = function (a) {
    const [f, rest] = opts(a, 'p');
    const { delay } = interval(rest);
    let rows = this.procs.filter(p => p.pid > 1);
    if (f.p && f.p !== 'ALL') rows = this.procs.filter(p => String(f.p).split(',').map(Number).includes(p.pid));
    const t = delay ? hms(this.clock + delay * 1000) : hms(this.clock), uid = u => u === 'root' ? 0 : u === 'www-data' ? 33 : 1000;
    let o = statHead(this) + '\n';
    if (f.r) o += `${t}      UID       PID  minflt/s  majflt/s     VSZ     RSS   %MEM  Command\n` + rows.map(p => `${t} ${pad(uid(p.user), 8)} ${pad(p.pid, 9)} ${pad((p.pid % 13 * 0.31).toFixed(2), 9)} ${pad('0.00', 9)} ${pad(8000 + p.pid % 900 * 7, 7)} ${pad(3000 + p.pid % 700 * 3, 7)} ${pad('0.04', 6)}  ${comm(p)}`).join('\n') + '\n';
    else if (f.d) o += `${t}      UID       PID   kB_rd/s   kB_wr/s kB_ccwr/s iodelay  Command\n` + rows.map(p => `${t} ${pad(uid(p.user), 8)} ${pad(p.pid, 9)} ${pad('0.00', 9)} ${pad((comm(p) === 'rsyslogd' || comm(p) === 'nginx' ? 1.37 : 0).toFixed(2), 9)} ${pad('0.00', 9)} ${pad(0, 7)}  ${comm(p)}`).join('\n') + '\n';
    else o += `${t}      UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command\n` + rows.map(p => { const u = p.cpu ? 99.0 : (p.pid % 7) * 0.02, sy = p.cpu ? 0.7 : u / 4; return `${t} ${pad(uid(p.user), 8)} ${pad(p.pid, 9)} ${pad(u.toFixed(2), 7)} ${pad(sy.toFixed(2), 7)} ${pad('0.00', 7)} ${pad('0.00', 7)} ${pad((u + sy).toFixed(2), 7)} ${pad(p.pid % 2, 5)}  ${comm(p)}`; }).join('\n') + '\n';
    this.out(o); if (delay) this.clock += delay * 1000; return 0;
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
  const SECURE_PATH = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin';
  C.sudo = function (a, input) {
    if (!a.length) { this.eout('usage: sudo command\n'); return 1; }
    if (a[0] === '-i' || a[0] === 'su' || a[0] === '-s') { this.user = 'root'; this.rootPath = this.vars.PATH; this.vars.PATH = SECURE_PATH; this.out('(you are now root. Type exit to go back to learner. Be careful, root can delete anything)\n'); return 0; }
    const keep = this.user, path = this.vars.PATH; this.user = 'root'; this.vars.PATH = SECURE_PATH;
    try { return this.call(a, input); } finally { this.user = keep; this.vars.PATH = path; }
  };
  C.su = function () { this.eout('su: Authentication failure (in this practice shell use sudo instead)\n'); return 1; };
  const exitRoot = C.exit;
  C.exit = function (a) { if (this.user === 'root') { this.user = USER; if (this.rootPath) { this.vars.PATH = this.rootPath; this.rootPath = null; } return 0; } return exitRoot.call(this, a); };
  ['dnf', 'wget', 'vim', 'vi', 'nano', 'htop', 'strace'].forEach(c => {
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
  /* ---------- systemd: units, systemctl and the journal (systemd 255 output) ---------- */
  const AUTH_EVENTS = (() => {
    const ev = [], t0 = T0 - 3 * 3600e3;
    const bad = [['203.0.113.7', 'admin'], ['203.0.113.7', 'root'], ['198.51.100.23', 'root'], ['203.0.113.7', 'test'], ['192.0.2.200', 'oracle'], ['198.51.100.23', 'root'], ['203.0.113.7', 'admin'], ['203.0.113.7', 'ubuntu'], ['198.51.100.23', 'pi'], ['203.0.113.7', 'root'], ['192.0.2.200', 'root'], ['203.0.113.7', 'guest']];
    let pid = 3100;
    bad.forEach(([ip, u], i) => {
      const t = t0 + i * 371e3 + (i % 3) * 17e3, real = u === 'root';
      ev.push({ t, id: `sshd[${pid}]`, unit: 'ssh.service', msg: real ? `Failed password for root from ${ip} port ${40000 + i * 211} ssh2` : `Invalid user ${u} from ${ip} port ${40000 + i * 211}`, prio: 6 });
      if (!real) ev.push({ t: t + 2000, id: `sshd[${pid}]`, unit: 'ssh.service', msg: `Failed password for invalid user ${u} from ${ip} port ${40000 + i * 211} ssh2`, prio: 6 });
      pid += 7;
    });
    ev.push({ t: t0 + 50 * 60e3, id: 'sshd[3402]', unit: 'ssh.service', msg: 'Accepted publickey for learner from 192.0.2.10 port 51515 ssh2: ED25519 SHA256:q2Y7v8dHkP0e3m1t5JZpLr4a9GxT6cUoWbNfK1sQe8A', prio: 6 });
    ev.push({ t: t0 + 50 * 60e3 + 1000, id: 'sshd[3402]', unit: 'ssh.service', msg: 'pam_unix(sshd:session): session opened for user learner(uid=1000) by learner(uid=0)', prio: 6 });
    ev.push({ t: t0 + 95 * 60e3, id: 'sudo', unit: '', msg: ' learner : TTY=pts/0 ; PWD=/home/learner ; USER=root ; COMMAND=/usr/bin/apt update', prio: 5 });
    ev.push({ t: t0 + 96 * 60e3, id: 'sudo', unit: '', msg: ' learner : TTY=pts/0 ; PWD=/home/learner ; USER=root ; COMMAND=/usr/bin/systemctl restart nginx', prio: 5 });
    ev.push({ t: t0 + 140 * 60e3, id: 'sudo', unit: '', msg: '    asha : 3 incorrect password attempts ; TTY=pts/1 ; PWD=/home/asha ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow', prio: 2 });
    return ev.sort((a, b) => a.t - b.t);
  })();
  const KERNEL_EVENTS = [
    { t: T0 - 3600e3, id: 'kernel', unit: '', msg: 'Linux version 6.8.0-practice (practice@brainy) #1 SMP', prio: 5, k: true },
    { t: T0 - 3600e3, id: 'kernel', unit: '', msg: 'Command line: BOOT_IMAGE=/boot/vmlinuz-6.8.0-practice root=UUID=b6e1c2a4-77aa-4e0f-9d3b-2f1c8a5e0d71 ro quiet', prio: 6, k: true },
    { t: T0 - 3600e3 + 2000, id: 'kernel', unit: '', msg: 'EXT4-fs (sda1): mounted filesystem b6e1c2a4-77aa-4e0f-9d3b-2f1c8a5e0d71 ro with ordered data mode. Quota mode: none.', prio: 6, k: true },
    { t: T0 - 25 * 60e3, id: 'kernel', unit: '', msg: 'usb 1-1: new high-speed USB device number 3 using xhci_hcd', prio: 6, k: true },
    { t: T0 - 25 * 60e3 + 900, id: 'kernel', unit: '', msg: 'sd 2:0:0:0: [sdb] 62529536 512-byte logical blocks: (32.0 GB/29.8 GiB)', prio: 5, k: true },
    { t: T0 - 4 * 60e3, id: 'kernel', unit: '', msg: 'Out of memory: Killed process 2261 (java) total-vm:4194304kB, anon-rss:3145728kB, file-rss:0kB, shmem-rss:0kB, UID:1001 pgtables:6400kB oom_score_adj:0', prio: 3, k: true }];
  const SSHD_CONFIG = '# This is the sshd server system-wide configuration file.  See\n# sshd_config(5) for more information.\n\nInclude /etc/ssh/sshd_config.d/*.conf\n\n#Port 22\n#ListenAddress 0.0.0.0\n\n#LoginGraceTime 2m\n#PermitRootLogin prohibit-password\n#MaxAuthTries 6\n\n#PubkeyAuthentication yes\n\n#PasswordAuthentication yes\n#PermitEmptyPasswords no\n\nKbdInteractiveAuthentication no\n\nUsePAM yes\n\nX11Forwarding yes\nPrintMotd no\n\nAcceptEnv LANG LC_* COLORTERM NO_COLOR\n\nSubsystem\tsftp\t/usr/lib/openssh/sftp-server\n';
  const UNITS0 = {
    'cron.service': { file: '/usr/lib/systemd/system/cron.service', pid: 618, data: '[Unit]\nDescription=Regular background program processing daemon\nDocumentation=man:cron(8)\nAfter=remote-fs.target nss-user-lookup.target\n\n[Service]\nEnvironmentFile=-/etc/default/cron\nExecStart=/usr/sbin/cron -f -P $EXTRA_OPTS\nKillMode=process\nRestart=on-failure\n\n[Install]\nWantedBy=multi-user.target\n' },
    'ssh.service': { file: '/usr/lib/systemd/system/ssh.service', pid: 412, data: '[Unit]\nDescription=OpenBSD Secure Shell server\nDocumentation=man:sshd(8) man:sshd_config(5)\nAfter=network.target auditd.service\n\n[Service]\nExecStartPre=/usr/sbin/sshd -t\nExecStart=/usr/sbin/sshd -D $SSHD_OPTS\nExecReload=/bin/kill -HUP $MAINPID\nKillMode=process\nRestart=on-failure\n\n[Install]\nWantedBy=multi-user.target\n' },
    'nginx.service': { file: '/usr/lib/systemd/system/nginx.service', pid: 905, data: '[Unit]\nDescription=A high performance web server and a reverse proxy server\nDocumentation=man:nginx(8)\nAfter=network.target\n\n[Service]\nType=forking\nPIDFile=/run/nginx.pid\nExecStartPre=/usr/sbin/nginx -t -q -g \'daemon on; master_process on;\'\nExecStart=/usr/sbin/nginx -g \'daemon on; master_process on;\'\nExecReload=/usr/sbin/nginx -g \'daemon on; master_process on;\' -s reload\n\n[Install]\nWantedBy=multi-user.target\n' },
    'backup.service': { file: '/etc/systemd/system/backup.service', failed: 23, data: '[Unit]\nDescription=Nightly backup\n\n[Service]\nType=oneshot\nExecStart=/usr/local/bin/backup.sh\n\n[Install]\nWantedBy=multi-user.target\n' }
  };
  const iniGet = (txt, key) => { const m = new RegExp('^' + key + '=(.*)$', 'm').exec(txt || ''); return m ? m[1].trim() : ''; };
  const sdDate = ms => { const d = new Date(ms), z = n => String(n).padStart(2, '0'); return `${DAYS3[d.getUTCDay()]} ${d.getUTCFullYear()}-${z(d.getUTCMonth() + 1)}-${z(d.getUTCDate())} ${z(d.getUTCHours())}:${z(d.getUTCMinutes())}:${z(d.getUTCSeconds())} UTC`; };
  const jDate = ms => { const d = new Date(ms), z = n => String(n).padStart(2, '0'); return `${MON3[d.getUTCMonth()]} ${z(d.getUTCDate())} ${z(d.getUTCHours())}:${z(d.getUTCMinutes())}:${z(d.getUTCSeconds())}`; };
  const ago = ms => { const s = Math.max(0, Math.round(ms / 1000)); if (s < 60) return s + 's'; const m = Math.floor(s / 60); if (m < 60) return m + 'min'; const h = Math.floor(m / 60); return h + 'h ' + (m % 60) + 'min'; };
  World.prototype.sd = function () {
    if (this.sdState) return this.sdState;
    const st = this.sdState = { units: {}, log: [], loaded: this.clock };
    this.mkdirs('/usr/lib/systemd/system'); this.mkdirs('/etc/systemd/system/multi-user.target.wants'); this.mkdirs('/usr/local/bin');
    if (!this.node('/etc/ssh/sshd_config')) { this.mkdirs('/etc/ssh/sshd_config.d'); this.mk('/etc/ssh/sshd_config', 'f', 0o644, 'root', SSHD_CONFIG); }
    const boot = T0 - 3600e3;
    Object.entries(UNITS0).forEach(([name, u]) => {
      if (!this.node(u.file)) this.mk(u.file, 'f', 0o644, 'root', u.data);
      const l = this.node('/etc/systemd/system/multi-user.target.wants/' + name, false); if (!l) this.mk('/etc/systemd/system/multi-user.target.wants/' + name, 'l', 0o777, 'root', u.file);
      st.units[name] = { state: u.failed ? 'failed' : 'active', since: u.failed ? T0 - 7 * 3600e3 + 5000 : boot, pid: u.pid, code: u.failed, mainPid: u.failed ? 4711 : u.pid, file: u.file };
      const desc = iniGet(u.data, 'Description');
      if (u.failed) {
        st.log.push({ t: T0 - 7 * 3600e3, id: 'systemd[1]', unit: name, msg: `Starting ${name} - ${desc}...` });
        st.log.push({ t: T0 - 7 * 3600e3 + 4000, id: 'backup.sh[4711]', unit: name, msg: 'rsync: [Receiver] mkdir "/mnt/backup/home" failed: No such file or directory (2)', prio: 3 });
        st.log.push({ t: T0 - 7 * 3600e3 + 4000, id: 'backup.sh[4711]', unit: name, msg: 'rsync error: error in file IO (code 11) at main.c(791) [Receiver=3.2.7]', prio: 3 });
        st.log.push({ t: T0 - 7 * 3600e3 + 5000, id: 'systemd[1]', unit: name, msg: `${name}: Main process exited, code=exited, status=23/n/a` });
        st.log.push({ t: T0 - 7 * 3600e3 + 5000, id: 'systemd[1]', unit: name, msg: `${name}: Failed with result 'exit-code'.`, prio: 4 });
        st.log.push({ t: T0 - 7 * 3600e3 + 5000, id: 'systemd[1]', unit: name, msg: `Failed to start ${name} - ${desc}.`, prio: 3 });
      } else {
        st.log.push({ t: boot, id: 'systemd[1]', unit: name, msg: `Starting ${name} - ${desc}...` });
        st.log.push({ t: boot, id: 'systemd[1]', unit: name, msg: `Started ${name} - ${desc}.` });
      }
    });
    ['/usr/sbin/cron', '/usr/sbin/sshd', '/usr/sbin/nginx'].forEach(f => { if (!this.node(f)) this.mk(f, 'f', 0o755, 'root', '#!practice ' + baseName(f) + '\n'); });
    AUTH_EVENTS.concat(KERNEL_EVENTS).forEach(e => st.log.push(Object.assign({}, e)));
    if (!this.node('/var/log/auth.log')) { const n = this.mk('/var/log/auth.log', 'f', 0o640, 'syslog', AUTH_EVENTS.map(e => `${jDate(e.t)} ${HOST} ${e.id}: ${e.msg}`).join('\n') + '\n'); n.group = 'adm'; }
    ['/var/log/syslog'].forEach(f => { const n = this.node(f); if (n) { n.owner = 'syslog'; n.group = 'adm'; } });
    if (!this.node('/usr/local/bin/backup.sh')) this.mk('/usr/local/bin/backup.sh', 'f', 0o755, 'root', '#!/bin/bash\nrsync -a /home/ /mnt/backup/home/\n');
    st.log.sort((a, b) => a.t - b.t);
    return st;
  };
  World.prototype.unitName = function (n) { return /\.(service|timer|socket|target|mount|path)$/.test(n) ? n : n + '.service'; };
  World.prototype.unitFile = function (name) { const st = this.sd(); const u = st.units[name]; if (u && this.node(u.file)) return u.file; for (const d of ['/etc/systemd/system', '/usr/lib/systemd/system']) if (this.node(d + '/' + name)) return d + '/' + name; return null; };
  World.prototype.unitData = function (name) { const f = this.unitFile(name); return f ? this.node(f).data : null; };
  World.prototype.unitEnabled = function (name) {
    const m = this.node('/etc/systemd/system/' + name, false); if (m && m.type === 'l' && m.target === '/dev/null') return 'masked';
    if (this.node('/etc/systemd/system/multi-user.target.wants/' + name, false)) return 'enabled';
    return /\[Install\]/.test(this.unitData(name) || '') ? 'disabled' : 'static';
  };
  World.prototype.sdLog = function (unit, id, msg, prio) { this.sd().log.push({ t: this.clock, id, unit, msg, prio }); };
  World.prototype.unitStart = function (name) {
    const st = this.sd(), data = this.unitData(name), desc = iniGet(data, 'Description') || name;
    const u = st.units[name] || (st.units[name] = { state: 'inactive', file: this.unitFile(name) });
    if (u.state === 'active') return 0;
    this.sdLog(name, 'systemd[1]', `Starting ${name} - ${desc}...`);
    const exec = iniGet(data, 'ExecStart').replace(/^[-@+!]+/, ''), prog = exec.split(/\s+/)[0], n = prog && this.node(prog);
    const pid = 3000 + Math.floor(this.clock / 1000) % 5000 + Object.keys(st.units).length;
    if (!prog || !n || !(n.mode & 0o111)) {
      Object.assign(u, { state: 'failed', since: this.clock, code: 203, mainPid: pid, pid: undefined, exec });
      this.sdLog(name, `(${baseName(prog || 'unknown')})[${pid}]`, `${name}: Unable to locate executable '${prog}': No such file or directory`, 3);
      this.sdLog(name, `(${baseName(prog || 'unknown')})[${pid}]`, `${name}: Failed at step EXEC spawning ${prog}: No such file or directory`, 3);
      this.sdLog(name, 'systemd[1]', `${name}: Main process exited, code=exited, status=203/EXEC`);
      this.sdLog(name, 'systemd[1]', `${name}: Failed with result 'exit-code'.`, 4);
      this.sdLog(name, 'systemd[1]', `Failed to start ${name} - ${desc}.`, 3);
      return 1;
    }
    const oneshot = iniGet(data, 'Type') === 'oneshot';
    if (oneshot) { Object.assign(u, { state: 'inactive', since: this.clock, ran: true, mainPid: pid, code: 0, exec }); this.sdLog(name, 'systemd[1]', `${name}: Deactivated successfully.`); this.sdLog(name, 'systemd[1]', `Finished ${name} - ${desc}.`); return 0; }
    Object.assign(u, { state: 'active', since: this.clock, pid, mainPid: pid, code: undefined, exec });
    const user = iniGet(data, 'User') || 'root';
    const nginx = name === 'nginx.service';
    this.procs.push({ pid, ppid: 1, user, cmd: nginx ? 'nginx: master process /usr/sbin/nginx -g daemon on; master_process on;' : exec, comm: baseName(prog), stat: 'S', ni: 0, start: this.clock });
    if (nginx) this.procs.push({ pid: pid + 1, ppid: pid, user: 'www-data', cmd: 'nginx: worker process', comm: 'nginx', stat: 'S', ni: 0, start: this.clock });
    this.sdLog(name, 'systemd[1]', `Started ${name} - ${desc}.`);
    return 0;
  };
  World.prototype.unitStop = function (name) {
    const st = this.sd(), u = st.units[name], desc = iniGet(this.unitData(name), 'Description') || name;
    if (!u || u.state !== 'active') { if (u && u.state === 'failed') { u.state = 'inactive'; } return 0; }
    this.sdLog(name, 'systemd[1]', `Stopping ${name} - ${desc}...`);
    this.procs = this.procs.filter(p => p.pid !== u.pid && p.ppid !== u.pid);
    Object.assign(u, { state: 'inactive', since: this.clock, pid: undefined });
    this.sdLog(name, 'systemd[1]', `${name}: Deactivated successfully.`);
    this.sdLog(name, 'systemd[1]', `Stopped ${name} - ${desc}.`);
    return 0;
  };
  C.systemctl = function (a) {
    const st = this.sd(), flags = a.filter(x => x.startsWith('-')), args = a.filter(x => !x.startsWith('-') && !/^(service|timer)$/.test(x) || false);
    const verb = args[0] || 'list-units', names = args.slice(1).map(n => this.unitName(n));
    const typeArg = (a.find(x => x.startsWith('--type=')) || '').split('=')[1] || (a.includes('-t') ? a[a.indexOf('-t') + 1] : '');
    const root = () => this.user === 'root';
    const deny = (what, n, see) => { this.eout(`Failed to ${what} ${n}: Interactive authentication required.\n${see ? `See system logs and 'systemctl status ${n}' for details.\n` : ''}`); return 1; };
    const exists = n => !!this.unitFile(n);
    const desc = n => iniGet(this.unitData(n), 'Description') || n;
    const sub = u => !u ? 'dead' : u.state === 'active' ? 'running' : u.state === 'failed' ? 'failed' : 'dead';
    const changed = n => { const f = this.unitFile(n); return f && st.units[n] && this.node(f).mtime > st.loaded; };
    const warnChanged = n => { if (changed(n)) this.eout(`Warning: The unit file, source configuration file or drop-ins of ${n} changed on disk. Run 'systemctl daemon-reload' to reload units.\n`); };
    if (verb === 'daemon-reload') { if (!root()) { this.eout('Failed to reload daemon: Interactive authentication required.\n'); return 1; } st.loaded = this.clock + 1; return 0; }
    if (['start', 'stop', 'restart', 'reload', 'try-restart'].includes(verb)) {
      if (!names.length) { this.eout(`Too few arguments.\n`); return 1; }
      let code = 0;
      for (const n of names) {
        if (!exists(n)) { this.eout(`Failed to ${verb} ${n}: Unit ${n} not found.\n`); code = 5; continue; }
        if (!root()) { code = deny(verb, n, verb !== 'stop'); continue; }
        if (this.unitEnabled(n) === 'masked') { this.eout(`Failed to ${verb} ${n}: Unit ${n} is masked.\n`); code = 1; continue; }
        warnChanged(n);
        if (verb === 'stop') this.unitStop(n);
        else if (verb === 'reload') { const u = st.units[n]; if (!u || u.state !== 'active') { this.eout(`${n} is not active, cannot reload.\n`); code = 1; } else if (!iniGet(this.unitData(n), 'ExecReload')) { this.eout(`Failed to reload ${n}: Job type reload is not applicable for unit ${n}.\n`); code = 1; } else this.sdLog(n, 'systemd[1]', `Reloaded ${n} - ${desc(n)}.`); }
        else { if (verb !== 'start') this.unitStop(n); if (this.unitStart(n)) { this.eout(`Job for ${n} failed because the control process exited with error code.\nSee "systemctl status ${n}" and "journalctl -xeu ${n}" for details.\n`); code = 1; } }
      }
      return code;
    }
    if (['enable', 'disable', 'mask', 'unmask'].includes(verb)) {
      let code = 0;
      for (const n of names) {
        if (!exists(n) && verb !== 'unmask') { this.eout(`Failed to ${verb} unit: Unit file ${n} does not exist.\n`); code = 1; continue; }
        if (!root()) { this.eout(`Failed to ${verb} unit: Interactive authentication required.\n`); code = 1; continue; }
        const wants = '/etc/systemd/system/multi-user.target.wants/' + n, f = this.unitFile(n);
        if (verb === 'enable') {
          if (!/\[Install\]/.test(this.unitData(n))) { this.eout(`The unit files have no installation config (WantedBy=, RequiredBy=, UpheldBy=,\nAlso=, or Alias= settings in the [Install] section, and DefaultInstance= for\ntemplate units). This means they are not meant to be enabled or disabled using systemctl.\n`); continue; }
          if (!this.node(wants, false)) { this.mk(wants, 'l', 0o777, 'root', f); this.out(`Created symlink ${wants} → ${f}.\n`); }
          if (a.includes('--now')) this.unitStart(n);
        } else if (verb === 'disable') {
          if (this.node(wants, false)) { this.removeNode(wants); this.out(`Removed "${wants}".\n`); }
          if (a.includes('--now')) this.unitStop(n);
        } else if (verb === 'mask') { const p = '/etc/systemd/system/' + n; if (!this.node(p, false)) { this.mk(p, 'l', 0o777, 'root', '/dev/null'); this.out(`Created symlink ${p} → /dev/null.\n`); } }
        else { const p = '/etc/systemd/system/' + n, m = this.node(p, false); if (m && m.type === 'l') { this.removeNode(p); this.out(`Removed "${p}".\n`); } }
      }
      return code;
    }
    if (verb === 'is-active' || verb === 'is-enabled' || verb === 'is-failed') {
      let code = 0;
      names.forEach(n => {
        const u = st.units[n];
        if (verb === 'is-enabled') { if (!exists(n)) { this.eout(`Failed to get unit file state for ${n}: No such file or directory\n`); code = 1; return; } const e = this.unitEnabled(n); this.out(e + '\n'); if (e !== 'enabled' && e !== 'static') code = 1; return; }
        const s2 = u ? u.state : 'inactive'; this.out(s2 + '\n');
        if (verb === 'is-active' ? s2 !== 'active' : s2 !== 'failed') code = verb === 'is-active' ? 3 : 1;
      });
      return code;
    }
    if (verb === 'cat') {
      let code = 0;
      names.forEach((n, i) => { const f = this.unitFile(n); if (!f) { this.eout(`No files found for ${n}.\n`); code = 1; return; } this.out(`${i ? '\n' : ''}# ${f}\n${this.node(f).data}`); });
      return code;
    }
    if (verb === 'status') {
      let code = 0;
      const list = names.length ? names : [];
      if (!list.length) { this.out(`● ${HOST}\n    State: ${Object.values(st.units).some(u => u.state === 'failed') ? 'degraded' : 'running'}\n    Units: ${Object.keys(st.units).length} loaded (incl. loaded aliases)\n     Jobs: 0 queued\n   Failed: ${Object.values(st.units).filter(u => u.state === 'failed').length} units\n    Since: ${sdDate(T0 - 3600e3)}; ${ago(this.clock - T0 + 3600e3)} ago\n`); return 0; }
      list.forEach((n, i) => {
        if (!exists(n)) { this.eout(`Unit ${n} could not be found.\n`); code = 4; return; }
        const u = st.units[n], data = this.unitData(n), en = this.unitEnabled(n);
        const mark = u && u.state === 'active' ? '●' : u && u.state === 'failed' ? '×' : '○';
        let o = `${i ? '\n' : ''}${mark} ${n} - ${desc(n)}\n     Loaded: ${en === 'masked' ? 'masked (Reason: Unit ' + n + ' is masked.)' : `loaded (${this.unitFile(n)}; ${en}; preset: enabled)`}\n`;
        if (changed(n)) o += `    Warning: The unit file, source configuration file or drop-ins of ${n} changed on disk. Run 'systemctl daemon-reload' to reload units.\n`;
        if (!u || (u.state === 'inactive' && !u.since)) o += '     Active: inactive (dead)\n';
        else if (u.state === 'active') o += `     Active: active (running) since ${sdDate(u.since)}; ${ago(this.clock - u.since)} ago\n`;
        else if (u.state === 'failed') o += `     Active: failed (Result: exit-code) since ${sdDate(u.since)}; ${ago(this.clock - u.since)} ago\n`;
        else o += `     Active: inactive (dead)${u.since ? ` since ${sdDate(u.since)}; ${ago(this.clock - u.since)} ago` : ''}\n`;
        const docs = iniGet(data, 'Documentation'); if (docs) o += `       Docs: ${docs.split(/\s+/).join('\n             ')}\n`;
        const exec = iniGet(data, 'ExecStart');
        if (u && u.state === 'failed') o += `    Process: ${u.mainPid} ExecStart=${exec} (code=exited, status=${u.code === 203 ? '203/EXEC' : u.code})\n   Main PID: ${u.mainPid} (code=exited, status=${u.code === 203 ? '203/EXEC' : u.code})\n`;
        else if (u && u.ran && u.state === 'inactive') o += `    Process: ${u.mainPid} ExecStart=${exec} (code=exited, status=0/SUCCESS)\n   Main PID: ${u.mainPid} (code=exited, status=0/SUCCESS)\n`;
        if (u && u.state === 'active') {
          const kids = this.procs.filter(p => p.ppid === u.pid);
          const me = this.procs.find(p => p.pid === u.pid);
          o += `   Main PID: ${u.pid} (${me ? me.comm || baseName(me.cmd.split(' ')[0]) : '?'})\n      Tasks: ${1 + kids.length} (limit: 4558)\n     Memory: ${(1.2 + kids.length * 1.6).toFixed(1)}M\n        CPU: ${12 + kids.length * 9}ms\n     CGroup: /system.slice/${n}\n`;
          const ps = [me].concat(kids).filter(Boolean);
          ps.forEach((p, j) => { o += `             ${j === ps.length - 1 ? '└─' : '├─'}${p.pid} ${/\s/.test(p.cmd) && /^nginx/.test(p.cmd) ? '"' + p.cmd + '"' : p.cmd}\n`; });
        }
        const lines = st.log.filter(e => e.unit === n).slice(-10);
        if (lines.length) o += '\n' + lines.map(e => `${jDate(e.t)} ${HOST} ${e.id}: ${e.msg}`).join('\n') + '\n';
        this.out(o);
        if (!u || u.state !== 'active') code = 3;
      });
      return code;
    }
    if (verb === 'list-units' || verb === 'list-unit-files' || (a.includes('--failed') && !args.length)) {
      const all = Object.keys(st.units).concat(this.node('/etc/systemd/system') ? Object.keys(this.node('/etc/systemd/system').kids).filter(k => /\.(service|timer)$/.test(k) && !st.units[k]) : []).sort();
      if (verb === 'list-unit-files') {
        const rows = all.filter(n => !typeArg || n.endsWith('.' + typeArg));
        const w = Math.max(9, ...rows.map(n => n.length));
        this.out(`${'UNIT FILE'.padEnd(w)} STATE    PRESET\n` + rows.map(n => `${n.padEnd(w)} ${this.unitEnabled(n).padEnd(8)} enabled`).join('\n') + `\n\n${rows.length} unit files listed.\n`);
        return 0;
      }
      const failedOnly = a.includes('--failed') || a.includes('--state=failed');
      const rows = all.filter(n => st.units[n] && (a.includes('--all') || st.units[n].state !== 'inactive') && (!failedOnly || st.units[n].state === 'failed') && (!typeArg || n.endsWith('.' + typeArg)));
      if (!rows.length) { this.out('  UNIT LOAD ACTIVE SUB DESCRIPTION\n\n0 loaded units listed.\n'); return 0; }
      const w = Math.max(4, ...rows.map(n => n.length));
      this.out(`  ${'UNIT'.padEnd(w)} LOAD   ACTIVE SUB     DESCRIPTION\n` + rows.map(n => { const u = st.units[n]; return `${u.state === 'failed' ? '●' : ' '} ${n.padEnd(w)} loaded ${u.state.padEnd(6)} ${sub(u).padEnd(7)} ${desc(n)}`; }).join('\n') +
        `\n\nLegend: LOAD   → Reflects whether the unit definition was properly loaded.\n        ACTIVE → The high-level unit activation state, i.e. generalization of SUB.\n        SUB    → The low-level unit activation state, values depend on unit type.\n\n${rows.length} loaded units listed.${failedOnly ? '' : ' Pass --all to see loaded but inactive units, too.\nTo show all installed unit files use \'systemctl list-unit-files\'.'}\n`);
      return 0;
    }
    if (verb === 'reboot' || verb === 'poweroff' || verb === 'halt') { this.eout(`The practice computer cannot ${verb}. On a real machine sudo systemctl ${verb} would ${verb === 'reboot' ? 'restart' : 'switch off'} it now.\n`); return 1; }
    if (verb === 'get-default') { this.out('multi-user.target\n'); return 0; }
    this.eout(`Unknown command verb '${verb}'.\n`); return 1;
  };
  C.journalctl = function (a) {
    const st = this.sd(); let rows = st.log.slice();
    if (this.user !== 'root') { this.eout("Hint: You are currently not seeing messages from other users and the system.\n      Users in groups 'adm', 'systemd-journal' can see all messages.\n      Pass -q to turn off this notice.\n"); this.out('-- No entries --\n'); return 0; }
    for (let i = 0; i < a.length; i++) {
      const x = a[i];
      if (x === '-u' || x === '--unit') { const n = this.unitName(a[++i]); rows = rows.filter(e => e.unit === n); }
      else if (/^-u./.test(x)) { const n = this.unitName(x.slice(2)); rows = rows.filter(e => e.unit === n); }
      else if (x === '-n' || x === '--lines') { const k = +a[++i]; rows = rows.slice(-k); }
      else if (/^-n\d+$/.test(x)) rows = rows.slice(-+x.slice(2));
      else if (x === '-p' || x === '--priority') { const lv = { emerg: 0, alert: 1, crit: 2, err: 3, warning: 4, notice: 5, info: 6, debug: 7 }; const p = a[++i], max = lv[p] !== undefined ? lv[p] : +p; rows = rows.filter(e => (e.prio !== undefined ? e.prio : 6) <= max); }
      else if (x === '--since' || x === '-S' || x === '--until' || x === '-U') {
        const v = String(a[++i] || '').trim(), base = this.clock - this.clock % 864e5; let t = NaN, m;
        if (v === 'today') t = base; else if (v === 'yesterday') t = base - 864e5; else if (v === 'now') t = this.clock;
        else if ((m = /^(\d+)\s*(min|minute|minutes|h|hour|hours) ago$/.exec(v))) t = this.clock - +m[1] * (m[2][0] === 'h' ? 36e5 : 6e4);
        else if ((m = /^(?:(\d{4})-(\d\d)-(\d\d)\s*)?(\d\d?):(\d\d)(?::(\d\d))?$/.exec(v))) t = m[1] ? Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5], +(m[6] || 0)) : base + (+m[4] * 3600 + +m[5] * 60 + +(m[6] || 0)) * 1000;
        else if ((m = /^(\d{4})-(\d\d)-(\d\d)$/.exec(v))) t = Date.UTC(+m[1], +m[2] - 1, +m[3]);
        if (isNaN(t)) { this.eout(`Failed to parse timestamp: ${v}\n`); return 1; }
        rows = rows.filter(e => (x === '--since' || x === '-S') ? e.t >= t : e.t <= t);
      }
      else if (x === '-g' || x === '--grep') { const re = new RegExp(a[++i], /[A-Z]/.test(a[i]) ? '' : 'i'); rows = rows.filter(e => re.test(e.msg)); }
      else if (x === '-k' || x === '--dmesg') rows = rows.filter(e => e.k);
      else if (/^_COMM=/.test(x)) { const c = x.slice(6); rows = rows.filter(e => e.id.split('[')[0] === c); }
      else if (/^SYSLOG_IDENTIFIER=/.test(x) || x === '-t') { const c = x === '-t' ? a[++i] : x.split('=')[1]; rows = rows.filter(e => e.id.split('[')[0] === c); }
      else if (x === '--disk-usage') { this.out('Archived and active journals take up 24.0M in the file system.\n'); return 0; }
      else if (x === '-o' || x === '--output') { if (a[++i] === 'cat') this.jcat = true; }
      else if (/^-[xebrfq]+$/.test(x) || x === '--no-pager' || x === '--reverse') { if (x.includes('r')) rows.reverse(); }
    }
    if (a.some(x => /^-[a-z]*f/.test(x) && x !== '--no-pager')) this.eout('(journalctl -f keeps waiting for new lines. The practice shell shows what is there now.)\n');
    if (!rows.length) { this.out('-- No entries --\n'); return 0; }
    const cat = this.jcat; this.jcat = false;
    this.out(rows.map(e => cat ? e.msg : `${jDate(e.t)} ${HOST} ${e.id}: ${e.msg}`).join('\n') + '\n');
    return 0;
  };
  /* dmesg: the kernel ring buffer, readable by root only (kernel.dmesg_restrict=1 on Ubuntu) */
  C.dmesg = function (a) {
    if (this.user !== 'root') { this.eout('dmesg: read kernel buffer failed: Operation not permitted\n'); return 1; }
    const boot = T0 - 3600e3, rows = this.sd().log.filter(e => e.k);
    this.out(rows.map(e => a.includes('-T') ? `[${sdDate(e.t).replace(/^(\w+) (\d+)-(\d+)-(\d+) (.*) UTC$/, (_, d, y, mo, da, hms) => `${d} ${MON3[+mo - 1]} ${+da} ${hms} ${y}`)}] ${e.msg}` : `[${((e.t - boot) / 1000 + 0.000001).toFixed(6).padStart(12)}] ${e.msg}`).join('\n') + '\n');
    return 0;
  };
  /* logger: write a line into the journal and the syslog */
  C.logger = function (a, input) {
    let tag = this.user, prio = 'user.notice'; const words = [];
    for (let i = 0; i < a.length; i++) { if (a[i] === '-t') tag = a[++i]; else if (a[i] === '-p') prio = a[++i]; else words.push(a[i]); }
    const msg = words.join(' ') || (input || '').replace(/\n$/, '');
    const lv = { emerg: 0, alert: 1, crit: 2, err: 3, error: 3, warning: 4, warn: 4, notice: 5, info: 6, debug: 7 }[prio.split('.').pop()];
    this.sd().log.push({ t: this.now(), id: tag, unit: '', msg, prio: lv === undefined ? 5 : lv });
    const sl = this.node('/var/log/syslog'); if (sl) sl.data += `${jDate(this.clock)} ${HOST} ${tag}: ${msg}\n`;
    return 0;
  };
  /* ---------- apt and dpkg: a small package database with real Ubuntu 24.04 (noble) data ---------- */
  /* name: [version, arch, installed KiB, summary, depends, download bytes, archive/component, files, multi-arch same, section] */
  const PKGDB = {
    bash: ['5.2.21-2ubuntu4', 'amd64', 1900, 'GNU Bourne Again SHell', [], 0, 'noble/main', ['/usr/bin/bash'], false, 'shells'],
    coreutils: ['9.4-3ubuntu6.3', 'amd64', 6944, 'GNU core utilities', [], 0, 'noble-updates/main', 'basename cat chmod chown cp cut date df dirname du echo env false head id ln ls mkdir mv nl printenv printf pwd readlink rm rmdir seq sleep sort stat tac tail tee test touch tr true uname uniq wc whoami yes'.split(' ').map(x => '/usr/bin/' + x), false, 'utils'],
    findutils: ['4.9.0-5build1', 'amd64', 552, 'utilities for finding files--find, xargs', [], 0, 'noble/main', ['/usr/bin/find', '/usr/bin/xargs'], false, 'utils'],
    grep: ['3.11-4build1', 'amd64', 344, 'GNU grep, egrep and fgrep', [], 0, 'noble/main', ['/usr/bin/grep'], false, 'utils'],
    gzip: ['1.12-1ubuntu3.2', 'amd64', 244, 'GNU compression utilities', [], 0, 'noble-updates/main', ['/usr/bin/gzip', '/usr/bin/gunzip', '/usr/bin/zcat'], false, 'utils'],
    passwd: ['1:4.13+dfsg1-4ubuntu3.2', 'amd64', 2419, 'change and administer password and group data', [], 0, 'noble-updates/main', ['/usr/bin/passwd', '/usr/bin/chage', '/usr/sbin/chpasswd', '/usr/sbin/groupadd', '/usr/sbin/groupdel', '/usr/sbin/useradd', '/usr/sbin/userdel', '/usr/sbin/usermod'], false, 'admin'],
    sed: ['4.9-2ubuntu0.24.04.1', 'amd64', 340, 'GNU stream editor for filtering/transforming text', [], 0, 'noble-updates/main', ['/usr/bin/sed'], false, 'utils'],
    sudo: ['1.9.15p5-3ubuntu5.24.04.4', 'amd64', 3472, 'Provide limited super user privileges to specific users', [], 0, 'noble-updates/main', ['/usr/bin/sudo'], false, 'admin'],
    tar: ['1.35+dfsg-3ubuntu0.4', 'amd64', 716, 'GNU version of the tar archiving utility', [], 0, 'noble-updates/main', ['/usr/bin/tar'], false, 'utils'],
    tree: ['2.1.1-2ubuntu3.24.04.2', 'amd64', 108, 'displays an indented directory tree, in color', [], 0, 'noble-updates/universe', ['/usr/bin/tree'], false, 'universe/utils'],
    cowsay: ['3.03+dfsg2-8', 'all', 91, 'configurable talking cow', ['libtext-charwidth-perl'], 18572, 'noble/universe', ['/usr/games/cowsay'], false, 'universe/games'],
    'libtext-charwidth-perl': ['0.04-11build3', 'amd64', 41, 'get display widths of characters on the terminal', [], 9358, 'noble/main', ['/usr/lib/x86_64-linux-gnu/perl5/5.38/Text/CharWidth.pm'], true, 'perl'],
    jq: ['1.7.1-3ubuntu0.24.04.2', 'amd64', 113, 'lightweight and flexible command-line JSON processor', ['libjq1'], 65694, 'noble-updates/main', ['/usr/bin/jq'], false, 'utils'],
    libjq1: ['1.7.1-3ubuntu0.24.04.2', 'amd64', 359, 'lightweight and flexible command-line JSON processor - shared library', ['libonig5'], 141902, 'noble-updates/main', ['/usr/lib/x86_64-linux-gnu/libjq.so.1'], true, 'utils'],
    libonig5: ['6.9.9-1build1', 'amd64', 629, 'regular expressions library', [], 172336, 'noble/main', ['/usr/lib/x86_64-linux-gnu/libonig.so.5'], true, 'libs'],
    figlet: ['2.2.5-3', 'amd64', 734, 'Make large character ASCII banners out of ordinary text', [], 133198, 'noble/universe', ['/usr/bin/figlet'], false, 'universe/text']
  };
  const BASE_PKGS = 'bash coreutils findutils grep gzip passwd sed sudo tar tree'.split(' ');
  const aptSize = b => { let x = b, i = 0; const u = ['B', 'kB', 'MB', 'GB']; for (;;) { if (x < 100 && i) return x.toFixed(1) + ' ' + u[i]; if (x < 10000) return Math.round(x) + ' ' + u[i]; x /= 1000; i++; } };
  World.prototype.pk = function () { if (!this.pkgs) { this.pkgs = {}; BASE_PKGS.forEach(n => { this.pkgs[n] = { auto: false }; }); } return this.pkgs; };
  const pkName = n => n + (PKGDB[n][8] ? ':' + PKGDB[n][1] : '');
  const aptHead = 'Reading package lists... Done\nBuilding dependency tree... Done\nReading state information... Done\n';
  const wrapList = names => '  ' + names.join(' ') + '\n';
  World.prototype.aptNeedRoot = function (lists) {
    if (this.user === 'root') return false;
    this.eout(lists ? 'E: Could not open lock file /var/lib/apt/lists/lock - open (13: Permission denied)\nE: Unable to lock directory /var/lib/apt/lists/\n' : 'E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)\nE: Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), are you root?\n');
    return true;
  };
  World.prototype.aptOrphans = function () {
    const inst = this.pk(), need = new Set();
    const keep = n => { if (need.has(n)) return; need.add(n); (PKGDB[n][4] || []).forEach(keep); };
    Object.keys(inst).filter(n => !inst[n].auto).forEach(keep);
    return Object.keys(inst).filter(n => !need.has(n)).sort();
  };
  World.prototype.aptConfirm = function (y, input) {
    if (y) return true;
    if (input && /^\s*[yY]/.test(input)) { this.out('Do you want to continue? [Y/n] Y\n'); return true; }
    this.out('Do you want to continue? [Y/n] Abort.\n'); return false;
  };
  World.prototype.aptFiles = function (n, add) {
    PKGDB[n][7].forEach(f => {
      if (add) { this.mkdirs(dirName(f)); if (!this.node(f)) this.mk(f, 'f', /\/s?bin\/|\/games\//.test(f) ? 0o755 : 0o644, 'root', /\/s?bin\/|\/games\//.test(f) ? '#!practice ' + baseName(f) + '\n' : '').mtime = this.now(); }
      else if (this.node(f)) this.removeNode(f);
    });
  };
  C.apt = C['apt-get'] = function (a, input) {
    const y = a.some(x => /^-[a-z]*y/.test(x) || x === '--yes' || x === '--assume-yes'), args = a.filter(x => !x.startsWith('-')), cmd = args[0], names = args.slice(1);
    const flags = a.filter(x => x.startsWith('--'));
    const inst = this.pk();
    if (!cmd) { this.out('apt 2.8.3 (amd64)\nUsage: apt [options] command\n\nMost used commands:\n  list - list packages based on package names\n  search - search in package descriptions\n  show - show package details\n  install - install packages\n  remove - remove packages\n  autoremove - automatically remove all unused packages\n  update - update list of available packages\n  upgrade - upgrade the system by installing/upgrading packages\n'); return 1; }
    if (cmd === 'update') {
      if (this.aptNeedRoot(true)) return 100;
      this.out('Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease\nHit:2 http://archive.ubuntu.com/ubuntu noble-updates InRelease\nHit:3 http://archive.ubuntu.com/ubuntu noble-backports InRelease\nHit:4 http://security.ubuntu.com/ubuntu noble-security InRelease\n' + aptHead + 'All packages are up to date.\n');
      this.aptUpdated = true; return 0;
    }
    if (cmd === 'upgrade' || cmd === 'full-upgrade' || cmd === 'dist-upgrade') {
      if (this.aptNeedRoot(false)) return 100;
      this.out(aptHead + 'Calculating upgrade... Done\n0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n'); return 0;
    }
    if (cmd === 'list') {
      const only = flags.includes('--installed'), up = flags.includes('--upgradable');
      this.out('Listing... Done\n');
      if (up) return 0;
      Object.keys(PKGDB).sort().filter(n => (!only || inst[n]) && (!names.length || names.some(g => new RegExp('^' + g.replace(/[.+]/g, '\\$&').replace(/\*/g, '.*') + '$').test(n)))).forEach(n => {
        const P = PKGDB[n], arch = P[6].split('/')[0];
        this.out(`${n}/${arch}${inst[n] ? ',now' : ''} ${P[0]} ${P[1]}${inst[n] ? (inst[n].auto ? ' [installed,automatic]' : ' [installed]') : ''}\n`);
      });
      return 0;
    }
    if (cmd === 'search') {
      const re = new RegExp(names.join('|') || '.', 'i');
      this.out('Sorting... Done\nFull Text Search... Done\n');
      Object.keys(PKGDB).sort().filter(n => re.test(n) || (!flags.includes('--names-only') && re.test(PKGDB[n][3]))).forEach(n => {
        const P = PKGDB[n]; this.out(`${n}/${P[6].split('/')[0]}${inst[n] ? ',now' : ''} ${P[0]} ${P[1]}${inst[n] ? (inst[n].auto ? ' [installed,automatic]' : ' [installed]') : ''}\n  ${P[3]}\n\n`);
      });
      return 0;
    }
    if (cmd === 'show') {
      let code = 0;
      names.forEach(n => {
        const P = PKGDB[n]; if (!P) { this.eout(`N: Unable to locate package ${n}\nE: No packages found\n`); code = 100; return; }
        const [suite, comp] = P[6].split('/'), host = suite === 'noble-security' ? 'security' : 'archive';
        this.out(`Package: ${n}\nVersion: ${P[0]}\nPriority: optional\nSection: ${P[9]}\nOrigin: Ubuntu\nInstalled-Size: ${aptSize(P[2] * 1024)}\n${P[4].length ? 'Depends: ' + P[4].join(', ') + '\n' : ''}${P[5] ? 'Download-Size: ' + aptSize(P[5]) + '\n' : ''}${inst[n] ? `APT-Manual-Installed: ${inst[n].auto ? 'no' : 'yes'}\n` : ''}APT-Sources: http://${host}.ubuntu.com/ubuntu ${suite}/${comp} amd64 Packages\nDescription: ${P[3]}\n\n`);
      });
      return code;
    }
    if (cmd === 'install' || cmd === 'reinstall') {
      if (this.aptNeedRoot(false)) return 100;
      if (!names.length) { this.out(aptHead + '0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n'); return 0; }
      const bad = names.find(n => !PKGDB[n]);
      if (bad) { this.out(aptHead); this.eout(`E: Unable to locate package ${bad}\n`); return 100; }
      this.out(aptHead);
      const add = [], seen = new Set();
      const want = n => { if (seen.has(n)) return; seen.add(n); PKGDB[n][4].forEach(want); if (!inst[n]) add.push(n); };
      names.forEach(n => {
        if (inst[n]) { this.out(`${n} is already the newest version (${PKGDB[n][0]}).\n`); if (inst[n].auto) { inst[n].auto = false; this.out(`${n} set to manually installed.\n`); } }
        want(n);
      });
      if (!add.length) { this.out('0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n'); return 0; }
      const extra = add.filter(n => !names.includes(n)).sort(), all = add.slice().sort();
      if (extra.length) this.out('The following additional packages will be installed:\n' + wrapList(extra));
      this.out('The following NEW packages will be installed:\n' + wrapList(all));
      const dl = add.reduce((t, n) => t + PKGDB[n][5], 0), kib = add.reduce((t, n) => t + PKGDB[n][2], 0);
      this.out(`0 upgraded, ${add.length} newly installed, 0 to remove and 0 not upgraded.\nNeed to get ${aptSize(dl)} of archives.\nAfter this operation, ${aptSize(kib * 1024)} of additional disk space will be used.\n`);
      if (extra.length && !this.aptConfirm(y, input)) return 1;
      add.forEach((n, i) => { const P = PKGDB[n], [suite, comp] = P[6].split('/'); this.out(`Get:${i + 1} http://archive.ubuntu.com/ubuntu ${suite}/${comp} amd64 ${n} ${P[1]} ${P[0]} [${aptSize(P[5])}]\n`); });
      this.out(`Fetched ${aptSize(dl)} in 0s (${aptSize(dl * 10)}/s)\n`);
      add.forEach(n => { const P = PKGDB[n]; this.out(`Selecting previously unselected package ${pkName(n)}.\nPreparing to unpack .../${n}_${P[0].replace(/^\d+:/, '')}_${P[1]}.deb ...\nUnpacking ${pkName(n)} (${P[0]}) ...\n`); });
      add.forEach(n => { this.out(`Setting up ${pkName(n)} (${PKGDB[n][0]}) ...\n`); inst[n] = { auto: !names.includes(n) }; this.aptFiles(n, true); });
      return 0;
    }
    if (cmd === 'remove' || cmd === 'purge' || cmd === 'autoremove') {
      if (this.aptNeedRoot(false)) return 100;
      if (cmd !== 'autoremove') { const bad = names.find(n => !PKGDB[n]); if (bad) { this.out(aptHead); this.eout(`E: Unable to locate package ${bad}\n`); return 100; } }
      this.out(aptHead);
      let gone = cmd === 'autoremove' ? this.aptOrphans() : names.filter(n => inst[n]);
      names.filter(n => PKGDB[n] && !inst[n]).forEach(n => this.out(`Package '${n}' is not installed, so not removed\n`));
      if (cmd !== 'autoremove' && flags.includes('--auto-remove')) { const keep = this.pkgs; const t = Object.assign({}, inst); gone.forEach(n => delete t[n]); this.pkgs = t; gone = gone.concat(this.aptOrphans()); this.pkgs = keep; }
      if (!gone.length) { this.out('0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.\n'); return 0; }
      if (cmd !== 'autoremove') {
        const t = Object.assign({}, inst); gone.forEach(n => delete t[n]); const keep = this.pkgs; this.pkgs = t; const orph = this.aptOrphans().filter(n => !gone.includes(n)); this.pkgs = keep;
        if (orph.length) this.out((orph.length > 1 ? 'The following packages were automatically installed and are no longer required:\n' : 'The following package was automatically installed and is no longer required:\n') + wrapList(orph) + `Use 'sudo apt autoremove' to remove ${orph.length > 1 ? 'them' : 'it'}.\n`);
      }
      const kib = gone.reduce((t, n) => t + PKGDB[n][2], 0);
      this.out('The following packages will be REMOVED:\n' + wrapList(gone.slice().sort().map(n => n + (cmd === 'purge' ? '*' : ''))) + `0 upgraded, 0 newly installed, ${gone.length} to remove and 0 not upgraded.\nAfter this operation, ${aptSize(kib * 1024)} disk space will be freed.\n`);
      if (!this.aptConfirm(y, input)) return 1;
      gone.forEach(n => { this.out(`Removing ${pkName(n)} (${PKGDB[n][0]}) ...\n`); delete inst[n]; this.aptFiles(n, false); });
      return 0;
    }
    this.eout(`E: Invalid operation ${cmd}\n`); return 100;
  };
  C['apt-cache'] = function (a) {
    const [cmd, ...names] = a.filter(x => !x.startsWith('-')), inst = this.pk();
    if (cmd === 'policy') { names.forEach(n => { const P = PKGDB[n]; if (!P) return; const [suite, comp] = P[6].split('/'); this.out(`${n}:\n  Installed: ${inst[n] ? P[0] : '(none)'}\n  Candidate: ${P[0]}\n  Version table:\n ${inst[n] ? '***' : '   '} ${P[0]} 500\n        500 http://archive.ubuntu.com/ubuntu ${suite}/${comp} amd64 Packages\n${inst[n] ? '        100 /var/lib/dpkg/status\n' : ''}`); }); return 0; }
    if (cmd === 'depends') { names.forEach(n => { const P = PKGDB[n]; if (!P) { this.eout(`E: No packages found\n`); return; } this.out(n + '\n' + P[4].map(d => `  Depends: ${d}\n`).join('')); }); return 0; }
    if (cmd === 'rdepends') { names.forEach(n => { this.out(`${n}\nReverse Depends:\n` + Object.keys(PKGDB).filter(m => PKGDB[m][4].includes(n)).map(m => `  ${m}\n`).join('')); }); return 0; }
    if (cmd === 'search') return C.apt.call(this, ['search'].concat(names));
    if (cmd === 'show') return C.apt.call(this, ['show'].concat(names));
    this.eout(`E: Invalid operation ${cmd || ''}\n`); return 100;
  };
  C.dpkg = C['dpkg-query'] = function (a) {
    const inst = this.pk(), op = a[0], names = a.slice(1);
    if (op === '-l') {
      const rows = (names.length ? names : Object.keys(inst).sort()).map(n => [n, inst[n] && PKGDB[n]]);
      const miss = rows.filter(r => !r[1]); const ok = rows.filter(r => r[1]);
      if (ok.length) {
        const w1 = Math.max(14, ...ok.map(r => r[0].length)), w2 = Math.max(15, ...ok.map(r => r[1][0].length));
        this.out(`Desired=Unknown/Install/Remove/Purge/Hold\n| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend\n|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)\n||/ ${'Name'.padEnd(w1)} ${'Version'.padEnd(w2)} Architecture Description\n+++-${'='.repeat(w1)}-${'='.repeat(w2)}-============-=================================\n`);
        ok.forEach(([n, P]) => this.out(`ii  ${n.padEnd(w1)} ${P[0].padEnd(w2)} ${P[1].padEnd(12)} ${P[3]}\n`));
      }
      miss.forEach(r => this.eout(`dpkg-query: no packages found matching ${r[0]}\n`));
      return miss.length ? 1 : 0;
    }
    if (op === '-L') { let code = 0; names.forEach(n => { if (!inst[n]) { this.eout(`dpkg-query: package '${n}' is not installed\nUse dpkg --contents (= dpkg-deb --contents) to list archive files contents.\n`); code = 1; } else { const dirs = new Set(['/.']); PKGDB[n][7].forEach(f => { let d = dirName(f); const up = []; while (d !== '/') { up.unshift(d); d = dirName(d); } up.forEach(x => dirs.add(x)); }); this.out([...dirs].concat(PKGDB[n][7]).join('\n') + '\n'); } }); return code; }
    if (op === '-S') { let code = 0; names.forEach(f => { const path = f.startsWith('/') ? f : null; const hit = Object.keys(inst).find(n => PKGDB[n][7].some(x => path ? x === path : baseName(x) === f)); if (hit) this.out(`${hit}: ${path || PKGDB[hit][7].find(x => baseName(x) === f)}\n`); else { this.eout(`dpkg-query: no path found matching pattern ${f}\n`); code = 1; } }); return code; }
    if (op === '-s' || op === '--status') { let code = 0; names.forEach(n => { const P = PKGDB[n]; if (!inst[n]) { this.eout(`dpkg-query: package '${n}' is not installed and no information is available\n`); code = 1; return; } this.out(`Package: ${n}\nStatus: install ok installed\nPriority: optional\nSection: ${P[9]}\nInstalled-Size: ${P[2]}\nArchitecture: ${P[1]}\nVersion: ${P[0]}\n${P[4].length ? 'Depends: ' + P[4].join(', ') + '\n' : ''}Description: ${P[3]}\n`); }); return code; }
    if (op === '-i' || op === '-r' || op === '-P') { if (this.user !== 'root') { this.eout('dpkg: error: requested operation requires superuser privilege\n'); return 2; } this.eout('dpkg: the practice shell has no .deb files. Use apt install, which downloads the .deb and calls dpkg for you.\n'); return 2; }
    this.eout('dpkg: error: need an action option\n\nType dpkg --help for help about installing and deinstalling packages [*];\nUse \'apt\' or \'aptitude\' for user-friendly package management;\nType dpkg -Dhelp for a list of dpkg debug flag values;\nType dpkg --force-help for a list of forcing options;\nType dpkg-deb --help for help about manipulating *.deb files;\n\nOptions marked [*] produce a lot of output - pipe it through \'less\' or \'more\' !\n'); return 2;
  };
  /* the programs the packages bring */
  C.figlet = function () { this.eout('figlet: the practice shell cannot draw the big letters. Try it on a real Linux machine.\n'); return 1; };
  C.cowsay = function (a, input) {
    const msg = (a.join(' ') || (input || '').replace(/\n$/, '')).replace(/\s+/g, ' ');
    const line = '_'.repeat(msg.length + 2), low = '-'.repeat(msg.length + 2);
    this.out(` ${line}\n< ${msg} >\n ${low}\n        \\   ^__^\n         \\  (oo)\\_______\n            (__)\\       )\\/\\\n                ||----w |\n                ||     ||\n`); return 0;
  };
  C.jq = function (a, input) {
    if (a[0] === '--version' || a[0] === '-V') { this.out('jq-1.7.1\n'); return 0; }
    const raw = a.includes('-r'), args = a.filter(x => !x.startsWith('-')), filt = args[0] || '.', file = args[1];
    let src = input || '';
    if (file) { const n = this.node(this.abs(file)); if (!n) { this.eout(`jq: error: Could not open ${file}: No such file or directory\n`); return 2; } src = n.data; }
    let data; try { data = JSON.parse(src); } catch (e) { this.eout('jq: error (at <stdin>:1): Cannot parse the input as JSON. The practice jq reads one JSON value.\n'); return 2; }
    const steps = filt === '.' ? [] : filt.replace(/^\./, '').split('.');
    let outs = [data];
    for (const st of steps) {
      const m = /^([\w-]*)(\[\])?$/.exec(st);
      if (!m) { this.eout(`jq: the practice jq understands paths such as .name, .a.b and .items[].name, not ${filt}\n`); return 3; }
      outs = outs.flatMap(v => { let x = m[1] ? (v === null || typeof v !== 'object' ? null : v[m[1]]) : v; if (x === undefined) x = null; return m[2] ? (Array.isArray(x) ? x : [x]) : [x]; });
    }
    outs.forEach(v => this.out((raw && typeof v === 'string' ? v : JSON.stringify(v, null, 2)) + '\n'));
    return 0;
  };
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
