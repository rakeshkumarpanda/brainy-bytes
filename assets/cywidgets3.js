/* ===== Complete Cybersecurity animations, part 3: Network and Systems, Application Security, Security Operations and Advanced. Built on MLZ.trace and CYZ (assets/cywidgets.js). ===== */

/* =====================================================================================================
   Network and Systems 1.1  ARP spoofing on a toy LAN, with no defence, Dynamic ARP Inspection or static entries
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const GW = 'aa:01', LAP = 'bb:05', ATK = 'cc:07';
  trace('cyarp', {
    title: 'ARP spoofing: how a man in the middle starts on a LAN',
    sub: 'ARP turns an IP address into a MAC address, and hosts believe any reply, even one they never asked for. The attacker tells the laptop "I am the gateway" and the gateway "I am the laptop". Choose a defence to see where it stops the lie.',
    W: 600, H: 340,
    params: [
      { k: 'def', label: 'Defence', type: 'select', v: 'none', opts: [['none', 'No defence'], ['dai', 'Switch: Dynamic ARP Inspection'], ['static', 'Laptop: static ARP entry for the gateway']] }
    ],
    tips: [
      { t: 'Play with no defence. Both caches are poisoned, and all the laptop’s traffic flows through the attacker.', play: true },
      { t: 'Turn on Dynamic ARP Inspection. The switch compares each reply with its DHCP snooping table and drops the forged ones.', set: { def: 'dai' }, play: true },
      { t: 'Try a static entry. The laptop ignores the lie, but the gateway can still be fooled, and static entries are hard to manage on big networks.', set: { def: 'static' }, play: true }
    ],
    frames(p) {
      const d = p.def;
      const fr = [];
      fr.push({ st: 1, lap: GW, gw: LAP, say: 'Normal state. The laptop (10.0.0.5) knows the gateway 10.0.0.1 is at MAC aa:01, and the gateway knows the laptop is at bb:05. Traffic goes laptop, switch, gateway.' });
      const lapFooled = d === 'none', gwFooled = d !== 'dai';
      fr.push({ st: 2, lap: GW, gw: LAP, msg: 1, say: `The attacker (10.0.0.7, MAC cc:07) sends the laptop an unasked ARP reply: "10.0.0.1 is at cc:07". ARP has no authentication, so nothing proves who sent it.` });
      fr.push({ st: 3, lap: lapFooled ? ATK : GW, gw: LAP, msg: 1, drop1: d === 'dai', ign1: d === 'static', say: d === 'none' ? 'The laptop overwrites its cache: the gateway is now at cc:07. Its next packets to the internet go to the attacker.' : d === 'dai' ? 'Dynamic ARP Inspection: the switch knows from DHCP snooping that 10.0.0.1 belongs to aa:01, so it drops the forged reply and logs it.' : 'The laptop has a static entry for 10.0.0.1, so it ignores the reply. Its cache stays correct.' });
      fr.push({ st: 4, lap: lapFooled ? ATK : GW, gw: gwFooled ? ATK : LAP, msg: 2, drop2: d === 'dai', say: gwFooled ? 'Now the attacker tells the gateway "10.0.0.5 is at cc:07". The gateway believes it, so replies for the laptop also go to the attacker.' : 'The second forged reply, to the gateway, is dropped by the switch as well.' });
      const mitm = lapFooled && gwFooled;
      fr.push({ st: 5, done: true, lap: lapFooled ? ATK : GW, gw: gwFooled ? ATK : LAP, mitm, half: !mitm && gwFooled, say: mitm ? 'Man in the middle: laptop to attacker to gateway, both ways. The attacker forwards packets so nothing seems wrong, and can read or change anything not protected by TLS. Tools such as arpwatch alert when an IP address changes MAC.' : !gwFooled ? 'Both lies were stopped at the switch. This is why managed switches with DHCP snooping and DAI are standard in offices, and why TLS still matters on every network.' : 'Half protected: the laptop is safe, but the gateway sends the laptop’s replies to the attacker, who can still read them. Defences must cover every host, which is why the switch is the better place.' });
      return fr.map(x => ({ ...x, d }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      const node = (x, y, name, ip, mac, fill) => cbox(z, x, y, 130, 50, [name, `${ip}  ${mac}`], { s: 12, b: true, fill });
      node(14, 20, 'Laptop', '10.0.0.5', LAP, col.surf);
      node(456, 20, 'Gateway', '10.0.0.1', GW, col.surf);
      node(235, 250, 'Attacker', '10.0.0.7', ATK, 'rgba(225,29,72,0.15)');
      cbox(z, 250, 120, 100, 34, f.d === 'dai' ? 'switch + DAI' : 'switch', { s: 12, b: true, mono: true, fill: f.d === 'dai' ? 'rgba(15,118,110,0.25)' : col.bg });
      D.line(g, 79, 70, 260, 120, col.line, 2); D.line(g, 521, 70, 340, 120, col.line, 2); D.line(g, 300, 154, 300, 250, col.line, 2);
      cbox(z, 14, 84, 150, 40, ['laptop cache', `10.0.0.1 → ${f.lap}`], { s: 11, b: true, mono: true, fill: f.lap === ATK ? 'rgba(225,29,72,0.2)' : col.bg });
      cbox(z, 436, 84, 150, 40, ['gateway cache', `10.0.0.5 → ${f.gw}`], { s: 11, b: true, mono: true, fill: f.gw === ATK ? 'rgba(225,29,72,0.2)' : col.bg });
      if (f.msg === 1 && f.st <= 3) { D.arrow(g, 260, 255, 150, 128, col.red, 2.5); cbox(z, 60, 178, 170, 26, '"10.0.0.1 is at cc:07"', { s: 11, b: true, mono: true, fill: col.surf, c: col.red }); }
      if (f.msg === 2) { D.arrow(g, 340, 255, 450, 128, col.red, 2.5); cbox(z, 370, 178, 170, 26, '"10.0.0.5 is at cc:07"', { s: 11, b: true, mono: true, fill: col.surf, c: col.red }); }
      if (f.drop1 || (f.drop2 && f.msg === 2)) cbox(z, 250, 162, 100, 24, 'DROPPED', { s: 12, b: true, fill: col.green, c: '#fff' });
      if (f.ign1) cbox(z, 14, 130, 150, 22, 'ignored (static)', { s: 11, b: true, fill: col.green, c: '#fff' });
      if (f.done) {
        if (f.mitm) { D.arrow(g, 120, 70, 255, 250, col.orange, 3); D.arrow(g, 345, 250, 480, 70, col.orange, 3); }
        cbox(z, 14, 306, 572, 28, f.mitm ? 'man in the middle: all traffic passes the attacker' : f.half ? 'half protected: replies to the laptop still pass the attacker' : 'attack stopped: caches stay correct', { s: 13, b: true, fill: f.mitm || f.half ? col.red : col.cv, c: '#fff' });
      }
    }
  });
})();

/* =====================================================================================================
   Network and Systems 1.1  A SYN flood filling the half open queue, with and without SYN cookies
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cysynflood', {
    title: 'SYN flood: filling the queue of half open connections',
    sub: 'Each SYN makes the server reserve a slot and wait up to 30 seconds for the final ACK. Forged SYNs never send it, so slots fill. With SYN cookies the server keeps no slot: it hides the state in its sequence number.',
    W: 600, H: 340,
    params: [
      { k: 'rate', label: 'Forged SYNs per second', type: 'range', v: 50, min: 0, max: 100, step: 5 },
      { k: 'ck', label: 'SYN cookies', type: 'select', v: 'off', opts: [['off', 'Off'], ['on', 'On']] }
    ],
    tips: [
      { t: 'Play at 50 forged SYNs a second with cookies off. After about 20 seconds the 1024 slots are full and real users are refused.', play: true },
      { t: 'Turn SYN cookies on. The queue still fills, but when it is full the server answers with cookies and real users still get in.', set: { ck: 'on' }, play: true },
      { t: 'Set 30 SYNs a second. 30 × 30 = 900 half open connections stay below 1024, so the server copes even without cookies.', set: { rate: 30, ck: 'off' }, play: true }
    ],
    frames(p) {
      const rate = +p.rate, ck = p.ck === 'on', B = 1024, T = 30, legit = 2;
      const fr = [{ st: 0, ticks: [], say: `Backlog of ${B} slots, timeout ${T} s. Forged SYNs arrive at ${rate} per second from random fake addresses, and real users at ${legit} per second.` }];
      const ticks = []; let served = 0, refused = 0;
      for (let t = 5; t <= 40; t += 5) {
        const half = Math.min(B, rate * Math.min(t, T));
        const full = half >= B;
        const ok = full && !ck ? 0 : legit * 5; served += ok; refused += legit * 5 - ok;
        ticks.push({ t, half, full });
        fr.push({ st: 1, ticks: ticks.slice(), served, refused, say: `t = ${t} s: ${rate} × ${Math.min(t, T)} = ${rate * Math.min(t, T)} forged half open connections${rate * Math.min(t, T) > B ? `, capped at ${B}` : ''}. ${full ? (ck ? 'Queue full, so the server switches to SYN cookies and real users still connect.' : 'Queue full: real users’ SYNs are dropped.') : 'Room left, real users connect.'}` });
      }
      fr.push({ st: 2, done: true, ticks, served, refused, say: refused ? `${refused} real connection attempts were refused. The steady state is rate × timeout = ${rate * T}, which is more than ${B}. Cutting the timeout, raising the backlog, SYN cookies and upstream filtering all help.` : `All ${served} real attempts got through. ${ck && rate * T >= B ? 'SYN cookies carried the load once the queue filled, at the cost of some TCP options.' : `rate × timeout = ${rate * T} stays below ${B}.`}` });
      return fr.map(x => ({ ...x, rate, ck, B }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, L = 50, Bm = 280, H = 230;
      D.line(g, L, Bm, 400, Bm, col.line, 1.5); D.line(g, L, Bm, L, Bm - H - 10, col.line, 1.5);
      D.line(g, L, Bm - H, 400, Bm - H, col.red, 1, [5, 4]); D.text(g, 'backlog 1024', 398, Bm - H - 5, { a: 'right', s: 10, b: true, c: col.red });
      D.text(g, 'half open', L - 6, Bm - H - 16, { s: 10, b: true, c: col.ink2 });
      f.ticks.forEach((k, i) => {
        const x = L + 10 + i * 42, h = k.half / f.B * H;
        D.rect(g, x, Bm - h, 30, h, { fill: k.full ? col.red : col.cv });
        D.text(g, `${k.t}s`, x + 15, Bm + 14, { a: 'center', s: 10, c: col.ink2 });
      });
      cbox(z, 450, 20, 136, 44, ['SYN cookies', f.ck ? 'ON' : 'OFF'], { s: 13, b: true, fill: f.ck ? 'rgba(15,118,110,0.25)' : col.bg });
      if (f.st >= 1) { cbox(z, 450, 80, 136, 44, ['real users in', String(f.served)], { s: 13, b: true, fill: col.surf }); cbox(z, 450, 134, 136, 44, ['refused', String(f.refused)], { s: 13, b: true, fill: f.refused ? 'rgba(225,29,72,0.2)' : col.surf }); }
      if (f.done) cbox(z, 14, 306, 572, 28, f.refused ? 'denial of service: real users refused' : 'service stayed up', { s: 13, b: true, fill: f.refused ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 1.1  How a port scan reads replies: SYN scan against connect scan on a pretend host
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const HOST = [[22, 'open', 'SSH'], [23, 'closed', 'Telnet'], [80, 'open', 'HTTP'], [445, 'filtered', 'SMB'], [3389, 'filtered', 'RDP'], [8080, 'closed', 'alt HTTP']];
  trace('cyscan', {
    title: 'Port scanning: what the replies mean',
    sub: 'A scanner sends a SYN to each port of a pretend host and reads the answer: SYN-ACK means open, RST means closed, silence means a firewall dropped it. Scan only systems you own or have written permission to test.',
    W: 600, H: 340,
    params: [
      { k: 'how', label: 'Scan type', type: 'select', v: 'syn', opts: [['syn', 'SYN scan (half open)'], ['connect', 'Connect scan (full handshake)']] }
    ],
    tips: [
      { t: 'Play the SYN scan. After a SYN-ACK the scanner sends RST, so the connection never completes and the service may not log it.', play: true },
      { t: 'Choose the connect scan. It finishes the handshake with ACK, so the service sees and logs a real connection.', set: { how: 'connect' }, play: true }
    ],
    frames(p) {
      const syn = p.how === 'syn';
      const rows = [];
      const fr = [{ st: 0, rows: [], say: `Scanning a pretend host with a ${syn ? 'SYN (half open) scan, which needs raw packet rights' : 'connect scan, which uses the normal connect() call any program can make'}. Nothing leaves this page.` }];
      HOST.forEach(([port, state, svc]) => {
        const reply = state === 'open' ? 'SYN-ACK' : state === 'closed' ? 'RST' : '(no reply)';
        const after = state === 'open' ? (syn ? 'send RST' : 'send ACK, then close') : state === 'filtered' ? 'retry, time out' : '';
        rows.push({ port, state, svc, reply, after });
        fr.push({ st: 1, rows: rows.slice(), say: `Port ${port} (${svc}): SYN sent, reply ${reply}. ${state === 'open' ? `Open: a service is listening. ${syn ? 'The scanner resets at once, so no connection is made.' : 'The scanner completes the handshake, so the service logs a connection.'}` : state === 'closed' ? 'Closed: the host is up but nothing listens on this port.' : 'Filtered: a firewall silently dropped the probe, so the scanner cannot tell what is behind it.'}` });
      });
      fr.push({ st: 2, done: true, rows, say: 'Result: 2 open, 2 closed, 2 filtered. Defenders close unused ports, filter the rest, and alert when one source touches many ports in a short time. Telnet sends passwords in clear text and should be off, and SMB and RDP should never face the internet.' });
      return fr.map(x => ({ ...x, syn }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      ['port', 'service', 'reply', 'scanner then', 'state'].forEach((h, i) => D.text(g, h, [20, 90, 200, 320, 490][i], 22, { s: 12, b: true, c: col.ink2 }));
      f.rows.forEach((r, i) => {
        const y = 32 + i * 40, c = r.state === 'open' ? col.green : r.state === 'closed' ? col.ink2 : col.orange;
        cbox(z, 14, y, 64, 32, String(r.port), { s: 13, b: true, mono: true, fill: col.surf });
        cbox(z, 84, y, 104, 32, r.svc, { s: 12, b: true, fill: col.bg });
        cbox(z, 194, y, 116, 32, r.reply, { s: 12, b: true, mono: true, fill: col.surf, c });
        cbox(z, 316, y, 160, 32, r.after || '-', { s: 11, b: true, fill: col.bg });
        cbox(z, 482, y, 104, 32, r.state, { s: 13, b: true, fill: c, c: '#fff' });
      });
      if (f.done) cbox(z, 14, 306, 572, 28, f.syn ? 'SYN scan: quieter, needs raw sockets' : 'connect scan: no special rights, logged by services', { s: 13, b: true, fill: col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 1.2  A packet walks down an ordered firewall rule list: first match wins, default deny
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const RULES = [['allow', 'tcp', '0.0.0.0/0', 443, 'HTTPS from anyone'], ['allow', 'tcp', '10.0.0.0/8', 22, 'SSH from the office'], ['deny', 'tcp', '0.0.0.0/0', 23, 'Telnet, log it']];
  const PK = { web: ['tcp', '203.0.113.5', 443], ssh_in: ['tcp', '10.1.2.3', 22], ssh_out: ['tcp', '203.0.113.5', 22], telnet: ['tcp', '198.51.100.7', 23], dns: ['udp', '203.0.113.5', 53] };
  const inNet = (ip, net) => { if (net === '0.0.0.0/0') return true; const [base, bits] = net.split('/'); const a = ip.split('.').map(Number), b = base.split('.').map(Number); let need = +bits; for (let i = 0; i < 4 && need > 0; i++, need -= 8) { const m = need >= 8 ? 255 : (0xff << (8 - need)) & 255; if ((a[i] & m) !== (b[i] & m)) return false; } return true; };
  trace('cyfirewall', {
    title: 'Firewall rules: first match wins',
    sub: 'A packet filter checks rules from the top. The first rule that matches decides, and a packet that matches nothing hits the default deny. Pick a packet and watch it walk down the list.',
    W: 600, H: 340,
    params: [
      { k: 'pk', label: 'Packet', type: 'select', v: 'ssh_out', opts: [['web', 'TCP 443 from 203.0.113.5'], ['ssh_in', 'TCP 22 from 10.1.2.3 (office)'], ['ssh_out', 'TCP 22 from 203.0.113.5 (internet)'], ['telnet', 'TCP 23 from 198.51.100.7'], ['dns', 'UDP 53 from 203.0.113.5']] }
    ],
    tips: [
      { t: 'Play SSH from the internet. It fails rule 1 (wrong port) and rule 2 (wrong source), so the default deny drops it.', play: true },
      { t: 'Try SSH from the office. Rule 2 matches, so it is allowed and rule 3 is never checked.', set: { pk: 'ssh_in' }, play: true },
      { t: 'Try UDP 53. No rule mentions UDP, so it falls through to the default deny, the safe choice.', set: { pk: 'dns' }, play: true }
    ],
    frames(p) {
      const [proto, src, port] = PK[p.pk];
      const fr = [{ st: 0, at: -1, res: [], say: `Packet: ${proto.toUpperCase()} from ${src} to port ${port}. The firewall checks the rules in order.` }];
      const res = []; let hit = -1;
      for (let i = 0; i < RULES.length; i++) {
        const [act, rp, net, rport] = RULES[i];
        const why = rp !== proto ? `protocol ${proto} is not ${rp}` : !inNet(src, net) ? `${src} is not in ${net}` : rport !== port ? `port ${port} is not ${rport}` : '';
        res.push(why ? 'no' : 'yes');
        fr.push({ st: 1, at: i, res: res.slice(), say: `Rule ${i + 1} (${act} ${rp} from ${net} to port ${rport}): ${why ? 'no match, because ' + why + '. Move on.' : `match, so the packet is <b>${act === 'allow' ? 'ALLOWED' : 'DENIED'}</b>. Later rules are not checked.`}` });
        if (!why) { hit = i; break; }
      }
      if (hit < 0) fr.push({ st: 1, at: 3, res: res.concat(['yes']), say: 'No rule matched, so the default rule applies: <b>DENY</b>. Default deny means anything not clearly allowed is blocked.' });
      const act = hit < 0 ? 'deny' : RULES[hit][0];
      fr.push({ st: 2, done: true, at: hit < 0 ? 3 : hit, res: fr[fr.length - 1].res, act, say: `Result: ${act === 'allow' ? 'allowed' : 'dropped'} by ${hit < 0 ? 'the default rule' : 'rule ' + (hit + 1)}. Order matters: if a broad allow rule sat above a narrow deny rule, the deny would never be reached, which is called shadowing.` });
      return fr.map(x => ({ ...x, proto, src, port }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 12, 572, 30, `packet: ${f.proto.toUpperCase()}  ${f.src}  →  port ${f.port}`, { s: 13, b: true, mono: true, fill: col.surf });
      const rows = RULES.map((r, i) => `${i + 1}. ${r[0].toUpperCase()} ${r[1]} from ${r[2]} port ${r[3]}`).concat(['default: DENY everything else']);
      rows.forEach((t, i) => {
        const y = 56 + i * 52, r = f.res[i];
        const fill = r === 'yes' ? ((i < 3 ? RULES[i][0] : 'deny') === 'allow' ? col.green : col.red) : r === 'no' ? col.bg : col.surf;
        cbox(z, 60, y, 400, 40, t, { s: 13, b: true, mono: true, fill, c: r === 'yes' ? '#fff' : r === 'no' ? col.ink2 : col.ink });
        if (r) cbox(z, 470, y, 116, 40, r === 'yes' ? 'match' : 'no match', { s: 12, b: true, fill: col.surf, c: r === 'yes' ? col.cv : col.ink2 });
        if (f.at === i) D.arrow(g, 18, y + 20, 54, y + 20, col.orange, 3);
      });
      if (f.done) cbox(z, 14, 306, 572, 28, f.act === 'allow' ? 'ALLOWED' : 'DROPPED', { s: 14, b: true, fill: f.act === 'allow' ? col.green : col.red, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 1.2  Anomaly detection: a z score threshold on login failures per minute
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const DATA = [4, 5, 3, 6, 4, 9, 5, 4, 30, 38, 4, 5, 7, 3, 8, 4], ATTACK = new Set([8, 9]), TRAIN = 6;
  const mean = DATA.slice(0, TRAIN).reduce((a, b) => a + b, 0) / TRAIN;
  const sd = Math.sqrt(DATA.slice(0, TRAIN).reduce((a, b) => a + (b - mean) ** 2, 0) / TRAIN);
  trace('cyids', {
    title: 'Anomaly detection: how far from normal is too far?',
    sub: 'The detector learns normal login failures per minute from the first 6 minutes, then alerts when a minute is more than k standard deviations above the mean. A password guessing burst hits minutes 9 and 10. Change k to trade missed attacks against false alarms.',
    W: 600, H: 340,
    params: [
      { k: 'th', label: 'Alert threshold k (z score)', type: 'range', v: 3, min: 1, max: 6, step: 0.5 }
    ],
    tips: [
      { t: 'Play with k = 3. The burst is caught and the busy minutes with 7 and 8 failures are not flagged.', play: true },
      { t: 'Set k = 1. Now the busy minute with 8 failures raises a false alarm. On a real network that means hundreds a day, and analysts start ignoring alerts.', set: { th: 1 }, play: true },
      { t: 'Set k = 6. Still caught here, but a slower attack of 15 failures a minute would now slip through.', set: { th: 6 }, play: true }
    ],
    frames(p) {
      const th = +p.th, cut = mean + th * sd;
      const fr = [{ st: 0, n: 0, say: `Training on minutes 1 to 6: mean = ${mean.toFixed(2)}, standard deviation = ${sd.toFixed(2)}. Alert line = mean + ${th} &times; sd = ${cut.toFixed(1)} failures.` }];
      let tp = 0, fp = 0, fn = 0;
      for (let i = TRAIN; i < DATA.length; i++) {
        const z = (DATA[i] - mean) / sd, alert = z > th, bad = ATTACK.has(i);
        if (alert && bad) tp++; else if (alert) fp++; else if (bad) fn++;
        fr.push({ st: 1, n: i + 1, tp, fp, fn, say: `Minute ${i + 1}: ${DATA[i]} failures, z = ${z.toFixed(1)}. ${alert ? (bad ? '<b>Alert</b>, and it really is the attack: a true positive.' : '<b>Alert</b>, but this was a normal busy minute: a false positive.') : (bad ? 'No alert, yet this was the attack: a false negative.' : 'Below the line, no alert.')}` });
      }
      fr.push({ st: 2, done: true, n: DATA.length, tp, fp, fn, say: `Totals: ${tp} true alerts, ${fp} false alarms, ${fn} missed. Lower k catches more but floods analysts. Higher k is quieter but misses slow attacks. Real systems also learn daily patterns and combine many signals.` });
      return fr.map(x => ({ ...x, th, cut }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, L = 40, R = 420, T = 20, B = 290, mx = 40;
      const Y = v => B - Math.min(v, mx) / mx * (B - T), bw = (R - L) / DATA.length;
      D.line(g, L, B, R, B, col.line, 1.5); D.line(g, L, T, L, B, col.line, 1.5);
      D.rect(g, L, T, bw * TRAIN, B - T, { fill: 'rgba(15,118,110,0.07)' });
      D.text(g, 'training', L + 4, T + 12, { s: 10, b: true, c: col.cv });
      const shown = Math.max(f.n, TRAIN);
      for (let i = 0; i < shown; i++) {
        const z0 = (DATA[i] - mean) / sd, alert = i >= TRAIN && z0 > f.th;
        D.rect(g, L + i * bw + 3, Y(DATA[i]), bw - 6, B - Y(DATA[i]), { fill: i < TRAIN ? col.ink2 : alert ? (ATTACK.has(i) ? col.red : col.orange) : col.cv });
        D.text(g, String(i + 1), L + i * bw + bw / 2, B + 13, { a: 'center', s: 9, c: col.ink2 });
      }
      D.line(g, L, Y(f.cut), R, Y(f.cut), col.red, 1.5, [6, 4]);
      D.text(g, `alert line ${f.cut.toFixed(1)}`, R - 2, Y(f.cut) - 5, { a: 'right', s: 10, b: true, c: col.red });
      if (f.st >= 1) {
        cbox(z, 440, 20, 146, 40, ['true alerts', String(f.tp)], { s: 12, b: true, fill: 'rgba(225,29,72,0.15)' });
        cbox(z, 440, 70, 146, 40, ['false alarms', String(f.fp)], { s: 12, b: true, fill: 'rgba(234,88,12,0.15)' });
        cbox(z, 440, 120, 146, 40, ['missed', String(f.fn)], { s: 12, b: true, fill: col.surf });
      }
      if (f.done) cbox(z, 14, 306, 572, 28, `k = ${f.th}: ${f.tp} caught, ${f.fp} false alarms, ${f.fn} missed`, { s: 13, b: true, fill: col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 1.2  What an eavesdropper on café Wi-Fi sees: no protection, TLS, or a VPN tunnel
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cyvpn', {
    title: 'What does an eavesdropper see? Plain, TLS and VPN',
    sub: 'The same web request leaves a laptop on café Wi-Fi. Step through the layers it is wrapped in and see what someone watching the Wi-Fi can still read. A VPN wraps the whole packet, encrypted, inside a new one addressed to the VPN gateway.',
    W: 600, H: 340,
    params: [
      { k: 'mode', label: 'Protection', type: 'select', v: 'vpn', opts: [['plain', 'None (plain HTTP)'], ['tls', 'HTTPS (TLS)'], ['vpn', 'VPN tunnel plus HTTPS']] }
    ],
    tips: [
      { t: 'Play the VPN. The watcher sees only the VPN gateway’s address, packet sizes and timing.', play: true },
      { t: 'Choose plain HTTP. Everything, including the password, is readable.', set: { mode: 'plain' }, play: true },
      { t: 'Choose HTTPS. The content is hidden, but the watcher still sees which server you talk to and usually its name.', set: { mode: 'tls' }, play: true }
    ],
    frames(p) {
      const m = p.mode;
      const fr = [{ st: 1, say: 'The browser builds a request: POST /login with user=asha and password=Sunrise7, for shop.example on port 443 or 80.' }];
      if (m !== 'plain') fr.push({ st: 2, say: 'TLS encrypts the HTTP request and protects it with an authentication tag. The TCP and IP headers outside it stay readable: they must, so routers can deliver it.' });
      if (m === 'vpn') fr.push({ st: 3, say: 'The VPN client encrypts the whole IP packet, headers included, and puts it inside a new UDP packet addressed to the VPN gateway (WireGuard uses port 51820 by default).' });
      const sees = m === 'plain' ? 'Everything: server address, the page, the user name and the password.' : m === 'tls' ? 'The server’s IP address and port, usually its name from the TLS handshake (SNI) or DNS, and sizes and timing. Not the page or the password.' : 'Only that the laptop talks to the VPN gateway, plus sizes and timing. The destination and its name are hidden inside the tunnel.';
      fr.push({ st: 4, done: true, say: `What the café Wi-Fi watcher sees: ${sees} ${m === 'vpn' ? 'The VPN provider, however, now sees what the café could have seen, so you move trust, you do not remove it.' : ''}` });
      return fr.map(x => ({ ...x, m }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, x0 = 120, w = 360;
      const red = 'rgba(225,29,72,0.18)', grn = 'rgba(15,118,110,0.22)';
      cbox(z, 14, 14, 90, 40, 'laptop', { s: 12, b: true, fill: col.surf });
      cbox(z, 496, 14, 90, 40, f.m === 'vpn' ? 'VPN gateway' : 'shop.example', { s: 11, b: true, fill: col.surf });
      D.arrow(g, 108, 34, 490, 34, col.line, 2);
      cbox(z, 230, 44, 140, 22, 'café Wi-Fi watcher', { s: 11, b: true, fill: col.surf, c: col.red });
      let y = 90;
      if (f.st >= 3) { cbox(z, x0 - 50, y, w + 100, 30, 'outer IP: laptop → VPN gateway | UDP 51820', { s: 12, b: true, mono: true, fill: red }); y += 36; }
      const enc3 = f.st >= 3;
      cbox(z, x0 - 20, y, w + 40, 30, 'IP: laptop → shop.example | TCP 443', { s: 12, b: true, mono: true, fill: enc3 ? grn : red, c: enc3 ? col.cv : col.ink }); y += 36;
      const enc2 = f.st >= 2;
      cbox(z, x0, y, w, 30, enc2 ? 'TLS record (encrypted)' : 'HTTP: POST /login', { s: 12, b: true, mono: true, fill: enc2 ? grn : red, c: enc2 ? col.cv : col.ink }); y += 36;
      cbox(z, x0 + 20, y, w - 40, 30, 'user=asha password=Sunrise7', { s: 12, b: true, mono: true, fill: enc2 ? grn : red, c: enc2 ? col.cv : col.ink });
      D.text(g, 'red: readable on the Wi-Fi   green: encrypted', 300, 286, { a: 'center', s: 11, b: true, c: col.ink2 });
      if (f.done) cbox(z, 14, 306, 572, 28, f.m === 'plain' ? 'everything readable' : f.m === 'tls' ? 'content hidden, server visible' : 'destination hidden, VPN gateway visible', { s: 13, b: true, fill: f.m === 'plain' ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 1.3  The WEP birthday problem: how quickly a random IV repeats
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cywep', {
    title: 'WEP’s 24 bit IV: the birthday paradox on Wi-Fi',
    sub: 'WEP mixed a 24 bit IV into the same key for every packet. When an IV repeats, the keystream repeats, and two ciphertexts XOR to the two plaintexts. P(repeat after n packets) ≈ 1 − e^(−n²/2N) with N = 2^bits.',
    W: 600, H: 340,
    params: [
      { k: 'bits', label: 'IV size in bits', type: 'select', v: '24', opts: [['24', '24 bits (WEP)'], ['32', '32 bits'], ['48', '48 bits (TKIP and CCMP packet numbers)']] }
    ],
    tips: [
      { t: 'Play 24 bits. A 50% chance of a repeat comes after only about 4823 packets, a few seconds on a busy network.', play: true },
      { t: 'Choose 48 bits. CCMP in WPA2 uses a 48 bit packet number that only counts up, so with a fresh key per session it never repeats.', set: { bits: '48' }, play: true }
    ],
    frames(p) {
      const b = +p.bits, N = 2 ** b, half = Math.sqrt(2 * Math.log(2) * N);
      const P = n => 1 - Math.exp(-n * n / (2 * N));
      const ns = [1000, 2000, 4823, 10000, 40000, 1e6, 2e7];
      const fr = [{ st: 0, pts: [], say: `IV space N = 2<sup>${b}</sup> = ${N.toLocaleString('en')}. Each packet picks an IV. How many packets until two share one?` }];
      const pts = [];
      ns.forEach(n => { pts.push([n, P(n)]); fr.push({ st: 1, pts: pts.slice(), say: `After ${n.toLocaleString('en')} packets: P(repeat) &asymp; 1 &minus; e<sup>&minus;n&sup2;/2N</sup> = <b>${(100 * P(n)).toFixed(P(n) < 0.001 ? 4 : 1)}%</b>.` }); });
      fr.push({ st: 2, done: true, pts, say: b === 24 ? `50% after &radic;(2 ln 2 &middot; N) &asymp; ${Math.round(half)} packets. An access point sending 1000 packets a second repeats IVs within seconds, and the FMS (2001) and PTW (2007) attacks went further and recovered the key itself from about 40000 to 85000 packets.` : `50% only after about ${Math.round(half).toLocaleString('en')} packets. ${b === 48 ? 'And WPA2 does not pick randomly: the packet number counts up and the key changes per session, so a nonce repeats only if an attack such as KRACK forces a reset.' : 'Better, but random 32 bit IVs would still repeat on a busy network within hours.'}` });
      return fr.map(x => ({ ...x, b, half }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, L = 50, R = 420, T = 20, B = 262;
      const lx = n => L + Math.log10(n) / Math.log10(2e7) * (R - L), Y = v => B - v * (B - T);
      D.line(g, L, B, R, B, col.line, 1.5); D.line(g, L, T, L, B, col.line, 1.5);
      [10, 1e3, 1e5, 1e7].forEach(n => D.text(g, n >= 1e6 ? `10^${Math.log10(n)}` : n.toLocaleString('en'), lx(n), B + 14, { a: 'center', s: 9, c: col.ink2 }));
      D.text(g, 'packets (log scale)', (L + R) / 2, B + 28, { a: 'center', s: 10, b: true, c: col.ink2 });
      [0, 0.5, 1].forEach(v => { D.text(g, `${v * 100}%`, L - 6, Y(v) + 4, { a: 'right', s: 9, c: col.ink2 }); D.line(g, L, Y(v), R, Y(v), col.line, 0.5, [3, 4]); });
      if (f.st >= 1) {
        const N = 2 ** f.b; let prev = null;
        for (let i = 0; i <= 100; i++) { const n = 10 ** (i / 100 * Math.log10(2e7)), pt = [lx(n), Y(1 - Math.exp(-n * n / (2 * N)))]; if (prev) D.line(g, prev[0], prev[1], pt[0], pt[1], 'rgba(15,118,110,0.35)', 2); prev = pt; }
      }
      f.pts.forEach(([n, v], i) => { D.circle(g, lx(n), Y(v), 5, { fill: i === f.pts.length - 1 ? col.red : col.cv }); });
      if (f.done && f.half < 2e7) { D.line(g, lx(f.half), B, lx(f.half), Y(0.5), col.red, 1.5, [5, 4]); D.text(g, `50% at ${Math.round(f.half)}`, lx(f.half) + 4, Y(0.5) - 6, { s: 10, b: true, c: col.red }); }
      cbox(z, 440, 20, 146, 44, ['IV bits', String(f.b)], { s: 13, b: true, fill: col.surf });
      if (f.pts.length) { const [n, v] = f.pts[f.pts.length - 1]; cbox(z, 440, 74, 146, 44, [`n = ${n.toLocaleString('en')}`, `P = ${(100 * v).toFixed(v < 0.001 ? 4 : 1)}%`], { s: 12, b: true, fill: col.bg }); }
      if (f.done) cbox(z, 14, 306, 572, 28, f.b === 24 ? 'WEP: keystreams repeat within seconds' : 'longer, counting nonces avoid repeats', { s: 13, b: true, fill: f.b === 24 ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 1.3  WPA2-PSK four way handshake against WPA3-SAE: can a captured handshake be cracked?
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cyhandshake', {
    title: 'WPA2 against WPA3: what a captured handshake gives away',
    sub: 'Both phone and access point know the Wi-Fi password. WPA2-Personal turns it straight into the master key, so a recorded handshake lets an attacker test guesses offline. WPA3 first runs SAE, a password authenticated key exchange with fresh secrets each time.',
    W: 600, H: 340,
    params: [
      { k: 'ver', label: 'Protocol', type: 'select', v: 'wpa2', opts: [['wpa2', 'WPA2-Personal (PSK)'], ['wpa3', 'WPA3-Personal (SAE)']] }
    ],
    tips: [
      { t: 'Play WPA2. The attacker records messages 1 and 2, then tries a word list at home until the MIC matches.', play: true },
      { t: 'Choose WPA3. The recorded SAE exchange depends on random secrets the attacker never sees, so each guess needs a live attempt that the access point can limit.', set: { ver: 'wpa3' }, play: true }
    ],
    frames(p) {
      const v2 = p.ver === 'wpa2';
      const m = v2 ? [
        ['both', 'PMK = PBKDF2(password, SSID, 4096) on both sides', 'Both sides turn the password into the 256 bit pairwise master key. The same password and SSID always give the same PMK.'],
        ['ap', 'msg 1: ANonce', 'The access point sends a random ANonce, in the clear.'],
        ['sta', 'msg 2: SNonce + MIC', 'The phone picks SNonce, computes PTK = PRF(PMK, MACs, ANonce, SNonce) and sends SNonce with a MIC made with part of the PTK.'],
        ['ap', 'msg 3: GTK (encrypted) + MIC', 'The access point derives the same PTK, checks the MIC, and sends the group key encrypted.'],
        ['sta', 'msg 4: ACK + MIC', 'The phone confirms. Both install the keys and start CCMP encryption.']
      ] : [
        ['both', 'password element PE = hash to curve(password, MACs)', 'Both sides map the password to a point on an elliptic curve. Nothing about it is sent.'],
        ['sta', 'SAE commit: scalar + element (fresh randoms)', 'The phone picks random secrets and sends a commit built from them and PE.'],
        ['ap', 'SAE commit: scalar + element (fresh randoms)', 'The access point does the same with its own random secrets.'],
        ['both', 'SAE confirm both ways, PMK = from the shared secret', 'Each side proves it derived the same secret. The PMK comes from a fresh Diffie-Hellman style secret, so it differs every time.'],
        ['both', '4 way handshake with that PMK', 'The usual 4 way handshake follows, now keyed by the fresh PMK.']
      ];
      const fr = [];
      m.forEach((r, i) => fr.push({ st: 1, n: i + 1, say: r[2] }));
      fr.push({ st: 2, done: true, n: m.length, say: v2 ? 'The attacker recorded messages 1 and 2 (or just the PMKID from message 1, Steube 2018). At home, for each word: PMK, then PTK, then MIC, and compare. GPUs test hundreds of thousands of words per second, so only a long random password is safe. And anyone who knows the password can decrypt recorded sessions.' : 'The recording is useless offline: checking a guess needs the random secrets inside the commits. Each guess means a live SAE attempt, which the access point can slow down. A fresh PMK every time also gives forward secrecy. Early implementations had side channel flaws (Dragonblood, 2019), fixed by later updates.' });
      return fr.map(x => ({ ...x, v2, m }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 12, 120, 34, 'phone', { s: 13, b: true, fill: col.surf }); cbox(z, 466, 12, 120, 34, 'access point', { s: 13, b: true, fill: col.surf });
      D.line(g, 74, 46, 74, 270, col.line, 1.5, [4, 4]); D.line(g, 526, 46, 526, 270, col.line, 1.5, [4, 4]);
      f.m.slice(0, f.n).forEach((r, i) => {
        const y = 62 + i * 42;
        if (r[0] === 'both') cbox(z, 90, y, 420, 30, r[1], { s: 11, b: true, mono: true, fill: col.bg });
        else { const ap = r[0] === 'ap'; D.arrow(g, ap ? 520 : 80, y + 26, ap ? 80 : 520, y + 26, col.cv, 2); cbox(z, 140, y, 320, 22, r[1], { s: 11, b: true, mono: true, fill: col.surf }); }
      });
      if (f.done) {
        cbox(z, 14, 278, 572, 22, f.v2 ? 'attacker: record, then guess offline at GPU speed' : 'attacker: recording gives nothing to test offline', { s: 11, b: true, fill: col.surf, c: f.v2 ? col.red : col.cv });
        cbox(z, 14, 306, 572, 28, f.v2 ? 'WPA2-PSK: offline dictionary attack possible' : 'WPA3-SAE: online guessing only, forward secrecy', { s: 13, b: true, fill: f.v2 ? col.red : col.cv, c: '#fff' });
      }
    }
  });
})();

/* =====================================================================================================
   Network and Systems 1.3  An evil twin access point against four kinds of Wi-Fi security
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cyeviltwin', {
    title: 'Evil twin: a fake access point with the same name',
    sub: 'Devices join the strongest signal with a known network name. An attacker sets up a twin of "CorpWiFi" close to the victim. Whether the twin gets anything depends on how the network authenticates.',
    W: 600, H: 340,
    params: [
      { k: 'sec', label: 'Network security', type: 'select', v: 'eapbad', opts: [['open', 'Open network'], ['psk', 'WPA2-PSK, password on the wall'], ['eapbad', '802.1X, certificate check OFF'], ['eap', '802.1X, certificate checked'], ['sae', 'WPA3-SAE, password secret']] }
    ],
    tips: [
      { t: 'Play 802.1X with the certificate check off. The phone talks to the twin’s fake RADIUS server and hands over a crackable login hash.', play: true },
      { t: 'Turn the certificate check on. The twin cannot show the company’s server certificate, so the phone refuses before sending anything.', set: { sec: 'eap' }, play: true },
      { t: 'Try a shared password on the wall. The attacker knows it too, so the twin works perfectly.', set: { sec: 'psk' }, play: true }
    ],
    frames(p) {
      const s = p.sec;
      const fr = [
        { st: 1, say: 'The real CorpWiFi access point is down the corridor, signal &minus;60 dBm.' },
        { st: 2, say: 'The attacker’s twin broadcasts the same name, CorpWiFi, right next to the victim at &minus;38 dBm. It may also send deauthentication frames to push devices off the real one (802.11w protection frames stop this, and WPA3 requires them).' },
        { st: 3, say: 'The phone sees a stronger CorpWiFi and tries to join it.' }
      ];
      const out = {
        open: ['joined', 'Open network: nothing proves who the access point is. The phone joins, and the twin sees all traffic not protected by TLS.'],
        psk: ['joined', 'The password is shared with everyone, including the attacker, so the twin completes the WPA2 handshake. A shared password authenticates the network to no one who also knows it.'],
        eapbad: ['leak', 'With the server certificate check off, the phone accepts the twin’s fake RADIUS server and runs PEAP with MSCHAPv2, giving the attacker a challenge and response that can be cracked offline to get the user’s password.'],
        eap: ['refused', 'The phone checks that the server certificate is the company’s, signed by the company CA, with the right name. The twin cannot show it, so the phone stops before sending credentials.'],
        sae: ['refused', 'The twin does not know the WPA3 password, so the SAE exchange fails, and it cannot learn the password by recording it.']
      }[s];
      fr.push({ st: 4, done: true, res: out[0], say: out[1] });
      return fr.map(x => ({ ...x, s }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      if (f.st >= 1) cbox(z, 440, 30, 146, 50, ['real CorpWiFi', '−60 dBm'], { s: 12, b: true, fill: col.surf });
      if (f.st >= 2) cbox(z, 220, 200, 160, 50, ['twin "CorpWiFi"', '−38 dBm'], { s: 12, b: true, fill: 'rgba(225,29,72,0.15)' });
      cbox(z, 14, 110, 120, 50, ['phone', 'saved: CorpWiFi'], { s: 12, b: true, fill: col.bg });
      if (f.st >= 3) { D.arrow(g, 134, 145, 220, 215, col.orange, 2.5); D.line(g, 134, 125, 440, 60, col.line, 1.5, [5, 5]); }
      if (f.done) {
        const bad = f.res !== 'refused';
        cbox(z, 400, 200, 186, 50, f.res === 'joined' ? ['joined the twin', 'traffic exposed'] : f.res === 'leak' ? ['login hash sent', 'crackable offline'] : ['refused', 'nothing sent'], { s: 12, b: true, fill: bad ? col.red : col.green, c: '#fff' });
        cbox(z, 14, 306, 572, 28, bad ? 'evil twin succeeds' : 'evil twin fails: the network proves who it is', { s: 13, b: true, fill: bad ? col.red : col.cv, c: '#fff' });
      }
    }
  });
})();

/* =====================================================================================================
   Network and Systems 2.1  TOTP step by step (RFC 6238 with HMAC-SHA-256, checked against the RFC vectors)
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D, sha256, utf8 } = CYZ;
  const hmac = (key, msg) => {
    let k = key.length > 64 ? sha256(key) : key.slice();
    while (k.length < 64) k.push(0);
    const ip = k.map(b => b ^ 0x36), op = k.map(b => b ^ 0x5c);
    return sha256(op.concat(sha256(ip.concat(msg))));
  };
  const hx = a => a.map(b => b.toString(16).padStart(2, '0')).join('');
  const KEY = utf8('12345678901234567890123456789012');
  trace('cytotp', {
    title: 'TOTP: how an authenticator app makes a code',
    sub: 'Phone and server share a secret key. Both count 30 second time slots since 1970, run HMAC on the slot number and cut the result down to a short code. These are the RFC 6238 SHA-256 test values, so you can check every step.',
    W: 600, H: 340,
    params: [
      { k: 't', label: 'Unix time (seconds)', type: 'select', v: '59', opts: [['59', '59'], ['1111111109', '1111111109'], ['1234567890', '1234567890'], ['2000000000', '2000000000']] },
      { k: 'dg', label: 'Digits', type: 'select', v: '8', opts: [['8', '8 (RFC test values)'], ['6', '6 (authenticator apps)']] }
    ],
    tips: [
      { t: 'Play t = 59 with 8 digits. The final code is 46119246, the value printed in RFC 6238.', play: true },
      { t: 'Switch to 6 digits. Apps keep the last 6 digits of the same number, so the code is 119246.', set: { dg: '6' }, play: true },
      { t: 'Try t = 1234567890. RFC 6238 lists 91819424 for SHA-256 at this time.', set: { t: '1234567890', dg: '8' }, play: true }
    ],
    frames(p) {
      const t = +p.t, dg = +p.dg, T = Math.floor(t / 30);
      const msg = []; let v = T; for (let i = 0; i < 8; i++) { msg.unshift(v % 256); v = Math.floor(v / 256); }
      const mac = hmac(KEY, msg), off = mac[31] & 15;
      const bin = ((mac[off] & 0x7f) * 16777216) + mac[off + 1] * 65536 + mac[off + 2] * 256 + mac[off + 3];
      const code = String(bin % 10 ** dg).padStart(dg, '0');
      const fr = [
        { st: 1, say: `Shared secret K (32 bytes of ASCII "1234...9012" in the RFC). Unix time t = ${t}.` },
        { st: 2, say: `Time slot T = floor(t / 30) = <b>${T}</b>, written as 8 bytes: ${hx(msg)}. Phone and server get the same T if their clocks agree within the slot.` },
        { st: 3, say: `HMAC-SHA-256(K, T) gives 32 bytes. Without K nobody can predict them, and old codes say nothing about new ones.` },
        { st: 4, say: `Dynamic truncation: the last byte is 0x${mac[31].toString(16).padStart(2, '0')}, its low 4 bits give offset = <b>${off}</b>. Take the 4 bytes starting there.` },
        { st: 5, say: `Those 4 bytes with the top bit cleared: ${hx(mac.slice(off, off + 4))} &rarr; <b>${bin}</b>.` },
        { st: 6, done: true, say: `Code = ${bin} mod 10<sup>${dg}</sup> = <b>${code}</b>. A guesser has a 1 in ${(10 ** dg).toLocaleString('en')} chance per try, so servers also limit attempts.` }
      ];
      return fr.map(x => ({ ...x, t, T, msg, mac, off, bin, code, dg }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 12, 280, 32, `K = ${hx(KEY.slice(0, 8))}...`, { s: 12, b: true, mono: true, fill: col.surf });
      cbox(z, 306, 12, 280, 32, `t = ${f.t}`, { s: 13, b: true, mono: true, fill: col.surf });
      if (f.st >= 2) cbox(z, 14, 54, 572, 32, `T = floor(t / 30) = ${f.T}  →  ${hx(f.msg)}`, { s: 12, b: true, mono: true, fill: col.bg });
      if (f.st >= 3) {
        D.text(g, 'HMAC-SHA-256(K, T)', 14, 106, { s: 11, b: true, c: col.ink2 });
        for (let i = 0; i < 32; i++) {
          const x = 14 + (i % 16) * 36, y = 114 + Math.floor(i / 16) * 32, hot = f.st >= 4 && i >= f.off && i < f.off + 4, last = f.st >= 4 && i === 31;
          cbox(z, x, y, 32, 26, f.mac[i].toString(16).padStart(2, '0'), { s: 11, b: true, mono: true, fill: hot ? col.cv : last ? col.orange : col.surf, c: hot || last ? '#fff' : col.ink });
        }
      }
      if (f.st >= 4) D.text(g, `offset = last byte & 0x0F = ${f.off}`, 14, 194, { s: 12, b: true, c: col.orange });
      if (f.st >= 5) cbox(z, 14, 206, 572, 32, `31 bit number: ${f.bin}`, { s: 13, b: true, mono: true, fill: col.bg });
      if (f.st >= 6) cbox(z, 150, 248, 300, 48, f.code, { s: 26, b: true, mono: true, fill: col.cv, c: '#fff' });
      if (f.done) cbox(z, 14, 306, 572, 28, 'same secret + same time slot = same code on phone and server', { s: 13, b: true, fill: col.surf, c: col.cv });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 2.1  A real time phishing relay against passwords, one time codes, push and passkeys
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cyphish', {
    title: 'Phishing relay: which second factor survives?',
    sub: 'The victim clicks a link to bank-example.login.test, a copy of the bank’s page run by the attacker, who passes everything to the real bank in real time. Choose the second factor and see if the attacker gets in.',
    W: 600, H: 340,
    params: [
      { k: 'f', label: 'Second factor', type: 'select', v: 'totp', opts: [['none', 'Password only'], ['totp', 'SMS or authenticator code'], ['push', 'Push approval'], ['number', 'Push with number matching'], ['passkey', 'Passkey (FIDO2 / WebAuthn)']] }
    ],
    tips: [
      { t: 'Play the authenticator code. The victim types it into the fake page and the attacker uses it within the same 30 seconds.', play: true },
      { t: 'Choose a passkey. The browser signs a challenge together with the real origin it sees, so the bank rejects the relayed answer.', set: { f: 'passkey' }, play: true },
      { t: 'Try plain push. Attackers send prompt after prompt until a tired user taps Approve, as in the 2022 Uber breach.', set: { f: 'push' }, play: true }
    ],
    frames(p) {
      const f = p.f;
      const fr = [
        { st: 1, say: 'An email says the account is locked. The link opens bank-example.login.test, which looks exactly like the bank.' },
        { st: 2, say: 'The victim types user name and password. The fake site forwards them to the real bank at once.' }
      ];
      const end = {
        none: [true, 'With a password only, the attacker is already logged in. The password may also be reused on other sites, which is credential stuffing.'],
        totp: [true, 'The bank asks for a code, the fake page asks the victim, and the attacker relays it within the 30 second window. Codes stop password reuse and guessing, but not a live relay. Tools such as Evilginx automate this and steal the session cookie too.'],
        push: [true, 'The attacker triggers a push to the victim’s phone, again and again. A tired or confused user taps Approve. This MFA fatigue attack was used against Uber in 2022.'],
        number: [true, 'Number matching shows a code on the login page that the user must type into the app. Fatigue spam fails, but a fake page can still show the real number and ask the user to type it, so a live relay still works. Better, but not phishing resistant.'],
        passkey: [false, 'The bank sends a challenge. The browser asks the passkey to sign it together with the origin it is really on: bank-example.login.test. The bank expects https://bank.example, so it rejects the answer. The user cannot be tricked into signing for the wrong site, because the browser fills in the origin.']
      }[f];
      if (f !== 'none') fr.push({ st: 3, say: f === 'passkey' ? 'The real bank sends a WebAuthn challenge. The attacker passes it to the fake page.' : f === 'totp' ? 'The real bank asks for a one time code. The fake page asks the victim for it.' : 'The real bank sends a push request to the victim’s phone.' });
      fr.push({ st: 4, done: true, ok: end[0], say: end[1] });
      return fr.map(x => ({ ...x, f }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 40, 130, 50, ['victim', 'browser'], { s: 13, b: true, fill: col.surf });
      cbox(z, 235, 40, 130, 50, ['fake site', 'login.test'], { s: 12, b: true, fill: 'rgba(225,29,72,0.15)' });
      cbox(z, 456, 40, 130, 50, ['real bank', 'bank.example'], { s: 12, b: true, fill: col.surf });
      if (f.st >= 1) D.arrow(g, 144, 65, 231, 65, col.orange, 2);
      if (f.st >= 2) { D.arrow(g, 365, 65, 452, 65, col.red, 2); cbox(z, 150, 104, 300, 26, 'user + password relayed', { s: 12, b: true, mono: true, fill: col.bg }); }
      if (f.st >= 3) cbox(z, 150, 140, 300, 26, f.f === 'passkey' ? 'challenge relayed, signed for login.test' : f.f === 'totp' ? 'code 482915 relayed in time' : 'push to phone', { s: 12, b: true, mono: true, fill: col.bg });
      if (f.done) {
        cbox(z, 150, 190, 300, 50, f.ok ? ['attacker logged in', 'session cookie stolen'] : ['bank rejects', 'wrong origin in signature'], { s: 13, b: true, fill: f.ok ? col.red : col.green, c: '#fff' });
        cbox(z, 14, 306, 572, 28, f.ok ? 'not phishing resistant' : 'phishing resistant: the origin is bound into the signature', { s: 13, b: true, fill: f.ok ? col.red : col.cv, c: '#fff' });
      }
    }
  });
})();

/* =====================================================================================================
   Network and Systems 2.1  Kerberos tickets, and the Kerberoasting attack on weak service passwords
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cykerberos', {
    title: 'Kerberos: tickets instead of passwords',
    sub: 'A trusted Key Distribution Centre (KDC) shares a long term key with every user and service. Users prove themselves once, get a ticket granting ticket (TGT), and trade it for service tickets. No password crosses the network.',
    W: 600, H: 340,
    params: [
      { k: 'v', label: 'Show', type: 'select', v: 'normal', opts: [['normal', 'Normal login'], ['roast', 'Kerberoasting attack']] }
    ],
    tips: [
      { t: 'Play the normal login: AS exchange, TGS exchange, then the file server opens the ticket with its own key.', play: true },
      { t: 'Show Kerberoasting. Any user can ask for a service ticket, and it is encrypted with a key made from the service account’s password, which can be guessed offline.', set: { v: 'roast' }, play: true }
    ],
    frames(p) {
      const roast = p.v === 'roast';
      const fr = roast ? [
        { st: 1, a: 'c2k', l: 'TGS-REQ for MSSQLSvc/db01', say: 'An attacker with any normal domain account asks the KDC for a ticket to a service, for example a database run under a user account.' },
        { st: 2, a: 'k2c', l: 'service ticket {…} key = from service password', say: 'The KDC happily returns it. The ticket is encrypted with a key derived from the service account’s password.' },
        { st: 3, a: 'off', l: 'offline: guess password → key → decrypt?', say: 'The attacker takes the ticket home and tries passwords until one decrypts it. No more traffic, no lockouts, no alarms.' },
        { st: 4, done: true, bad: true, say: 'Defences: long random service passwords (25 or more characters) or group managed service accounts that rotate automatically, AES only (no RC4), and alerts on unusual ticket requests. A stolen krbtgt key is worse still: it lets attackers forge any TGT, a golden ticket.' }
      ] : [
        { st: 1, a: 'c2k', l: 'AS-REQ: "I am asha" + timestamp', say: 'AS exchange: Asha asks for a TGT. Pre authentication encrypts a timestamp with her password derived key, so the KDC knows she has it.' },
        { st: 2, a: 'k2c', l: 'TGT {asha, S1} krbtgt + {S1} asha', say: 'The KDC returns a TGT, encrypted with its own krbtgt key, and session key S1 encrypted with Asha’s key. Only the real Asha can open S1.' },
        { st: 3, a: 'c2k', l: 'TGS-REQ: TGT + authenticator {time} S1', say: 'TGS exchange: to reach the file server she shows the TGT and an authenticator made with S1. Her password is not needed again until the TGT expires, typically after 10 hours.' },
        { st: 4, a: 'k2c', l: 'ticket {asha, S2} files + {S2} S1', say: 'The KDC returns a service ticket encrypted with the file server’s key, and session key S2 for Asha.' },
        { st: 5, a: 'c2s', l: 'AP-REQ: ticket + authenticator {time} S2', say: 'AP exchange: the file server opens the ticket with its own key, finds S2, and checks the authenticator. It never contacts the KDC. Clocks must agree within about 5 minutes, which stops old authenticators being replayed.' },
        { st: 6, done: true, bad: false, say: 'Single sign on: one password entry, many services, and no password on the wire. Kerberos came from MIT’s Project Athena in the 1980s and is the heart of Microsoft Active Directory logins.' }
      ];
      return fr.map((x, i) => ({ ...x, roast, log: fr.slice(0, i + 1).filter(y => y.l) }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 60, 120, 54, [f.roast ? 'attacker' : 'Asha', f.roast ? '(any user)' : 'client'], { s: 13, b: true, fill: f.roast ? 'rgba(225,29,72,0.15)' : col.surf });
      cbox(z, 240, 8, 120, 54, ['KDC', 'AS + TGS'], { s: 13, b: true, fill: col.surf });
      cbox(z, 466, 60, 120, 54, [f.roast ? 'db01' : 'file server', 'service'], { s: 13, b: true, fill: col.surf });
      const path = { c2k: [134, 72, 236, 44], k2c: [236, 50, 134, 82], c2s: [134, 100, 462, 100] }[f.a];
      if (path) D.arrow(g, path[0], path[1], path[2], path[3], col.orange, 3);
      f.log.forEach((y, i) => {
        const cur = i === f.log.length - 1 && !f.done;
        cbox(z, 14, 128 + i * 34, 572, 28, `${i + 1}. ${y.l}`, { s: 11, b: true, mono: true, fill: y.a === 'off' ? 'rgba(225,29,72,0.15)' : cur ? 'rgba(15,118,110,0.18)' : col.bg });
      });
      if (f.done) cbox(z, 14, 306, 572, 28, f.bad ? 'weak service passwords fall to offline guessing' : 'logged in to the service without sending a password', { s: 13, b: true, fill: f.bad ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 2.2  The access matrix, read by columns (ACLs) or by rows (capability lists)
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const S = ['asha', 'ravi', 'build'], O = ['payroll', 'wiki', 'repo'];
  const M = { asha: { payroll: 'rw', wiki: 'rw', repo: '' }, ravi: { payroll: 'r', wiki: 'r', repo: '' }, build: { payroll: '', wiki: 'r', repo: 'r' } };
  trace('cymatrix', {
    title: 'The access matrix: ACLs or capabilities?',
    sub: 'Rows are subjects, columns are objects, and each cell holds the rights. Real systems never store the whole matrix. They store either each column with its object (an access control list) or each row with its subject (a capability list).',
    W: 600, H: 340,
    params: [
      { k: 'view', label: 'Store the matrix as', type: 'select', v: 'acl', opts: [['acl', 'ACLs (columns, kept with each object)'], ['cap', 'Capabilities (rows, kept with each subject)']] }
    ],
    tips: [
      { t: 'Play ACLs. Each file keeps its own list, so "who can read payroll?" is one lookup, and revoking one user from one file is easy.', play: true },
      { t: 'Choose capabilities. Each subject carries its rights like keys, so "what can ravi reach?" is one lookup, and passing a right on is easy, but revoking it is hard.', set: { view: 'cap' }, play: true }
    ],
    frames(p) {
      const acl = p.view === 'acl';
      const fr = [{ st: 1, hi: -1, say: 'The full matrix: 3 subjects by 3 objects. r = read, w = write, an empty cell means no rights. Real systems have millions of each, and most cells are empty.' }];
      const items = acl ? O : S;
      items.forEach((it, i) => {
        const list = acl ? S.filter(s => M[s][it]).map(s => `${s}: ${M[s][it]}`) : O.filter(o => M[it][o]).map(o => `${o}: ${M[it][o]}`);
        fr.push({ st: 2, hi: i, say: acl ? `Column "${it}" becomes its ACL: ${list.join(', ') || 'empty'}. The object carries it, like the permission bits and ACL of a file.` : `Row "${it}" becomes its capability list: ${list.join(', ') || 'empty'}. The subject carries these like keys, such as open file descriptors or signed tokens.` });
      });
      fr.push({ st: 3, done: true, hi: -1, say: acl ? 'ACLs: easy to review and revoke per object, the model of Unix, Windows and cloud storage policies. Hard to answer "everything this user can reach" without scanning every object.' : 'Capabilities: easy to delegate and to check without a central lookup, the model of file descriptors, object capability systems and many bearer tokens. Hard to revoke once handed out.' });
      return fr.map(x => ({ ...x, acl }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, x0 = 120, y0 = 50, cw = 100, ch = 50;
      O.forEach((o, j) => cbox(z, x0 + j * cw, y0 - 36, cw - 6, 30, o, { s: 13, b: true, fill: f.acl && f.hi === j ? col.cv : col.surf, c: f.acl && f.hi === j ? '#fff' : col.ink }));
      S.forEach((s, i) => {
        cbox(z, 14, y0 + i * ch, 96, ch - 6, s, { s: 13, b: true, fill: !f.acl && f.hi === i ? col.cv : col.surf, c: !f.acl && f.hi === i ? '#fff' : col.ink });
        O.forEach((o, j) => {
          const on = f.st === 2 && (f.acl ? f.hi === j : f.hi === i);
          cbox(z, x0 + j * cw, y0 + i * ch, cw - 6, ch - 6, M[s][o] || '·', { s: 15, b: true, mono: true, fill: on ? 'rgba(15,118,110,0.25)' : col.bg });
        });
      });
      if (f.st >= 2) {
        const items = f.acl ? O : S, upto = f.st === 3 ? items.length - 1 : f.hi;
        for (let i = 0; i <= upto; i++) {
          const it = items[i];
          const list = f.acl ? S.filter(s => M[s][it]).map(s => `${s}:${M[s][it]}`) : O.filter(o => M[it][o]).map(o => `${o}:${M[it][o]}`);
          cbox(z, 432, 14 + i * 56, 154, 48, [f.acl ? `ACL ${it}` : `caps ${it}`, list.join(' ') || '(none)'], { s: 11, b: true, mono: true, fill: col.surf });
        }
      }
      if (f.done) cbox(z, 14, 306, 572, 28, f.acl ? 'ACL: "who can access this object?" is quick' : 'capability: "what can this subject access?" is quick', { s: 13, b: true, fill: col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 2.2  Bell-LaPadula (no read up, no write down) against Biba (no read down, no write up)
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const LV = ['Unclassified', 'Confidential', 'Secret', 'Top Secret'];
  trace('cyblp', {
    title: 'Bell-LaPadula and Biba: which way may information flow?',
    sub: 'A subject at one level checks reads and writes against objects at every level. Bell-LaPadula protects secrecy, so information may only flow up. Biba protects integrity, so information may only flow down.',
    W: 600, H: 340,
    params: [
      { k: 'm', label: 'Model', type: 'select', v: 'blp', opts: [['blp', 'Bell-LaPadula (secrecy)'], ['biba', 'Biba (integrity)']] },
      { k: 'lv', label: 'Subject level', type: 'range', v: 2, min: 0, max: 3, step: 1 }
    ],
    tips: [
      { t: 'Play Bell-LaPadula for a Secret subject. It may read Secret and below, and write Secret and above, so secrets never leak down.', play: true },
      { t: 'Switch to Biba. The arrows flip: read only at or above your level, write only at or below, so untrusted data never contaminates trusted data.', set: { m: 'biba' }, play: true },
      { t: 'Set the level to Unclassified under Bell-LaPadula. It may write anywhere above, a blind write up, but read only Unclassified.', set: { m: 'blp', lv: 0 }, play: true }
    ],
    frames(p) {
      const blp = p.m === 'blp', s = +p.lv;
      const fr = [{ st: 0, rows: [], say: `Subject at level <b>${LV[s]}</b>. ${blp ? 'Bell-LaPadula (1973): simple security property, no read up, and star property, no write down.' : 'Biba (1977): simple integrity, no read down, and star integrity, no write up. Levels now mean trustworthiness.'}` }];
      const rows = [];
      for (let o = 3; o >= 0; o--) {
        const r = blp ? s >= o : o >= s, w = blp ? o >= s : s >= o;
        rows.push({ o, r, w });
        fr.push({ st: 1, rows: rows.slice(), say: `Object at ${LV[o]}: read ${r ? 'allowed' : 'denied'}, write ${w ? 'allowed' : 'denied'}. ${blp ? (o > s ? 'Reading would reveal higher secrets.' : o < s ? 'Writing down could leak secrets into lower files.' : 'Same level: both allowed.') : (o < s ? 'Reading could pull in untrusted data.' : o > s ? 'Writing up could corrupt more trusted data.' : 'Same level: both allowed.')}` });
      }
      fr.push({ st: 2, done: true, rows, say: blp ? 'Information can only move up the lattice. A Trojan horse running with this subject’s rights cannot copy a secret into a lower file. The cost: writing up blind, and no way to downgrade without a trusted subject.' : 'Information can only move down. Windows integrity levels follow this idea: a low integrity browser tab cannot write to medium or high integrity files and processes.' });
      return fr.map(x => ({ ...x, blp, s }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      D.text(g, f.blp ? 'secrecy level' : 'integrity level', 14, 20, { s: 11, b: true, c: col.ink2 });
      for (let o = 3; o >= 0; o--) {
        const y = 30 + (3 - o) * 66;
        cbox(z, 14, y, 160, 54, f.blp ? LV[o] : ['Low', 'Medium', 'High', 'System'][o], { s: 13, b: true, fill: o === f.s ? 'rgba(15,118,110,0.25)' : col.surf });
        const row = f.rows.find(r => r.o === o);
        if (row) {
          cbox(z, 190, y + 6, 120, 42, row.r ? 'read ✓' : 'read ✗', { s: 13, b: true, fill: row.r ? col.green : col.red, c: '#fff' });
          cbox(z, 320, y + 6, 120, 42, row.w ? 'write ✓' : 'write ✗', { s: 13, b: true, fill: row.w ? col.green : col.red, c: '#fff' });
        }
      }
      cbox(z, 456, 30 + (3 - f.s) * 66, 130, 54, ['subject', f.blp ? LV[f.s] : ['Low', 'Medium', 'High', 'System'][f.s]], { s: 12, b: true, fill: col.cv, c: '#fff' });
      if (f.done) cbox(z, 14, 306, 572, 28, f.blp ? 'Bell-LaPadula: information flows only up' : 'Biba: information flows only down', { s: 13, b: true, fill: col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 2.2  RBAC: users get roles, roles get permissions, seniors inherit, conflicts are refused
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const ROLES = { employee: ['read wiki', 'submit expense'], manager: ['approve expense'], accountant: ['pay expense', 'read ledger'] };
  const JUN = { manager: ['employee'], accountant: ['employee'] };
  trace('cyrbac', {
    title: 'Role based access control',
    sub: 'Permissions are given to roles, and users are given roles. Senior roles inherit junior roles. A separation of duties rule stops one person holding two roles that together allow fraud.',
    W: 600, H: 340,
    params: [
      { k: 'q', label: 'Question', type: 'select', v: 'approve', opts: [['approve', 'Can asha approve an expense?'], ['pay', 'Can asha pay an expense?'], ['wiki', 'Can ravi read the wiki?'], ['both', 'Make asha accountant too']] }
    ],
    tips: [
      { t: 'Play "can asha approve?". asha is a manager, and managers hold approve expense.', play: true },
      { t: 'Ask "can ravi read the wiki?". ravi is an accountant, which inherits employee, which holds read wiki.', set: { q: 'wiki' }, play: true },
      { t: 'Try to make asha an accountant too. Approving and paying the same expense must be split, so the assignment is refused.', set: { q: 'both' }, play: true }
    ],
    frames(p) {
      const q = p.q;
      const fr = [{ st: 1, say: 'Users: asha is a manager, ravi is an accountant. Roles: employee (read wiki, submit expense), manager (approve expense), accountant (pay expense, read ledger). Manager and accountant both inherit employee.' }];
      if (q === 'both') {
        fr.push({ st: 2, hl: ['asha', 'manager', 'accountant'], say: 'Request: add the accountant role to asha, who is already a manager.' });
        fr.push({ st: 3, done: true, ok: false, hl: ['manager', 'accountant'], say: 'Refused by static separation of duties: manager and accountant are mutually exclusive, because one person could then approve and pay their own expense claim. This is the RBAC version of the Clark-Wilson idea of separating duties.' });
      } else {
        const user = q === 'wiki' ? 'ravi' : 'asha', perm = { approve: 'approve expense', pay: 'pay expense', wiki: 'read wiki' }[q];
        const role = user === 'asha' ? 'manager' : 'accountant';
        fr.push({ st: 2, hl: [user, role], say: `${user} has the role ${role}.` });
        const direct = ROLES[role].includes(perm), inh = !direct && JUN[role].some(j => ROLES[j].includes(perm));
        fr.push({ st: 3, hl: [user, role].concat(inh ? ['employee'] : []).concat([perm]), say: direct ? `${role} holds "${perm}" directly.` : inh ? `${role} does not hold "${perm}", but it inherits employee, which does.` : `Neither ${role} nor the roles it inherits hold "${perm}".` });
        fr.push({ st: 4, done: true, ok: direct || inh, hl: [user, role].concat(inh ? ['employee'] : []).concat([perm]), say: direct || inh ? `Allowed. Change the role once and every manager or accountant changes with it, which is why RBAC scales.` : `Denied. To let asha pay, an admin would need to give her the accountant role, which separation of duties forbids.` });
      }
      return fr.map(x => ({ ...x, q, hl: x.hl || [] }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, H = new Set(f.hl);
      const U = { asha: [14, 60], ravi: [14, 170] }, R = { manager: [210, 30], accountant: [210, 130], employee: [210, 230] };
      const P = { 'approve expense': [430, 20], 'pay expense': [430, 72], 'read ledger': [430, 124], 'read wiki': [430, 176], 'submit expense': [430, 228] };
      D.line(g, 124, 82, 210, 52, col.line, 2); D.line(g, 124, 192, 210, 152, col.line, 2);
      D.line(g, 210, 52, 192, 52, col.ink2, 1.5, [4, 4]); D.line(g, 192, 52, 192, 252, col.ink2, 1.5, [4, 4]); D.arrow(g, 192, 252, 208, 252, col.ink2, 1.5); D.arrow(g, 275, 174, 275, 228, col.ink2, 1.5);
      D.text(g, 'inherits', 280, 206, { s: 10, b: true, c: col.ink2 });
      Object.entries(ROLES).forEach(([r, ps]) => ps.forEach(pp => D.line(g, R[r][0] + 130, R[r][1] + 22, P[pp][0], P[pp][1] + 18, H.has(r) && H.has(pp) ? col.cv : col.line, H.has(r) && H.has(pp) ? 3 : 1)));
      Object.entries(U).forEach(([u, [x, y]]) => cbox(z, x, y, 110, 44, u, { s: 13, b: true, fill: H.has(u) ? col.cv : col.surf, c: H.has(u) ? '#fff' : col.ink }));
      Object.entries(R).forEach(([r, [x, y]]) => cbox(z, x, y, 130, 44, r, { s: 13, b: true, fill: H.has(r) ? 'rgba(15,118,110,0.3)' : col.bg }));
      Object.entries(P).forEach(([pp, [x, y]]) => cbox(z, x, y, 156, 36, pp, { s: 12, b: true, mono: true, fill: H.has(pp) ? 'rgba(15,118,110,0.3)' : col.surf }));
      if (f.q === 'both' && f.st >= 2) D.line(g, 124, 82, 210, 152, col.red, 2.5, [6, 4]);
      if (f.done) cbox(z, 14, 306, 572, 28, f.ok ? 'allowed through the role' : f.q === 'both' ? 'refused: separation of duties' : 'denied: no role grants it', { s: 13, b: true, fill: f.ok ? col.green : col.red, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 3.1  Worm outbreak curves: SI and SIR models with a cleanup rate
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cyworm', {
    title: 'Worm outbreaks: the epidemic curve',
    sub: 'A scanning worm infects new hosts in proportion to infected × still vulnerable: dI/dt = β·I·S/N. Defenders clean hosts at rate γ. When R0 = β/γ is below 1 the outbreak dies out. Numbers based on SQL Slammer: 75000 hosts, doubling every 8.5 seconds.',
    W: 600, H: 340,
    params: [
      { k: 'dbl', label: 'Doubling time at the start', type: 'select', v: '8.5', opts: [['8.5', '8.5 s (Slammer, 2003)'], ['37', '37 minutes (Code Red, 2001)']] },
      { k: 'g', label: 'Cleanup rate γ (fraction of β)', type: 'select', v: '0', opts: [['0', 'none'], ['0.25', 'γ = β/4 (R0 = 4)'], ['1.25', 'γ = 1.25β (R0 = 0.8)']] }
    ],
    tips: [
      { t: 'Play Slammer with no cleanup. The S shaped curve passes 90% in under 3 minutes, faster than any human response.', play: true },
      { t: 'Set R0 = 4. Cleaning helps, but most hosts are still infected at some point. Patching before the outbreak is what really works.', set: { g: '0.25' }, play: true },
      { t: 'Set R0 = 0.8. Each infection causes less than one more on average, so the worm fizzles out.', set: { g: '1.25' }, play: true }
    ],
    frames(p) {
      const N = 75000, dblS = p.dbl === '8.5' ? 8.5 : 37 * 60, beta = Math.log(2) / dblS, gamma = beta * +p.g;
      const Tend = dblS * 30, steps = 3000, dt = Tend / steps;
      let S = N - 1, I = 1, R = 0; const pts = [[0, I, R]];
      for (let k = 1; k <= steps; k++) { const ni = beta * S * I / N * dt, nr = gamma * I * dt; S -= ni; I += ni - nr; R += nr; if (k % 30 === 0) pts.push([k * dt, I, R]); }
      const fmt = t => dblS < 60 ? `${Math.round(t)} s` : `${(t / 3600).toFixed(1)} h`;
      const fr = [{ st: 0, n: 1, say: `N = 75000 vulnerable hosts, one infected. β = ln 2 / ${p.dbl === '8.5' ? '8.5 s' : '37 min'}${gamma ? `, γ = ${p.g}β, R0 = ${(1 / +p.g).toFixed(1)}` : ', no cleanup'}.` }];
      [10, 25, 40, 55, 70, 85, 100].forEach(pc => {
        const n = Math.round(pts.length * pc / 100); const [t, i, r] = pts[n - 1];
        fr.push({ st: 1, n, say: `t = ${fmt(t)}: ${Math.round(i).toLocaleString('en')} infected now${gamma ? `, ${Math.round(r).toLocaleString('en')} cleaned` : ''} (${(100 * (i + r) / N).toFixed(1)}% ever infected).` });
      });
      const ever = (pts[pts.length - 1][1] + pts[pts.length - 1][2]) / N;
      fr.push({ st: 2, done: true, n: pts.length, ever, say: gamma === 0 ? `Nearly every vulnerable host is infected. Early growth is exponential, then it slows as vulnerable hosts run out, the logistic S curve. Slammer reached about 90% of vulnerable hosts in 10 minutes.` : +p.g > 1 ? `R0 &lt; 1: the outbreak dies out with only ${(ever * 100).toFixed(2)}% ever infected.` : `R0 = 4: ${(ever * 100).toFixed(0)}% are infected at some point. Cleanup lowers the peak but the real defence is having fewer vulnerable hosts before the worm arrives.` });
      return fr.map(x => ({ ...x, pts, N, Tend, fmt }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, L = 50, R = 420, T = 20, B = 262;
      const X = t => L + t / f.Tend * (R - L), Y = v => B - v / f.N * (B - T);
      D.line(g, L, B, R, B, col.line, 1.5); D.line(g, L, T, L, B, col.line, 1.5);
      [0, 0.5, 1].forEach(v => D.text(g, `${v * 100}%`, L - 6, Y(v * f.N) + 4, { a: 'right', s: 9, c: col.ink2 }));
      D.text(g, `time (0 to ${f.fmt(f.Tend)})`, (L + R) / 2, B + 18, { a: 'center', s: 10, b: true, c: col.ink2 });
      const pts = f.pts.slice(0, f.n);
      for (let i = 1; i < pts.length; i++) {
        D.line(g, X(pts[i - 1][0]), Y(pts[i - 1][1]), X(pts[i][0]), Y(pts[i][1]), col.red, 2.5);
        D.line(g, X(pts[i - 1][0]), Y(pts[i - 1][2]), X(pts[i][0]), Y(pts[i][2]), col.green, 2);
        D.line(g, X(pts[i - 1][0]), Y(pts[i - 1][1] + pts[i - 1][2]), X(pts[i][0]), Y(pts[i][1] + pts[i][2]), col.ink2, 1.2, [4, 3]);
      }
      cbox(z, 440, 20, 146, 30, 'infected now', { s: 12, b: true, fill: 'rgba(225,29,72,0.2)' });
      cbox(z, 440, 56, 146, 30, 'cleaned', { s: 12, b: true, fill: 'rgba(22,163,74,0.2)' });
      cbox(z, 440, 92, 146, 30, 'ever infected (dashed)', { s: 11, b: true, fill: col.surf });
      if (f.done) cbox(z, 14, 306, 572, 28, `ever infected: ${(f.ever * 100).toFixed(1)}% of vulnerable hosts`, { s: 13, b: true, fill: f.ever > 0.5 ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 3.1  Byte histograms and Shannon entropy: spotting packed or encrypted data
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D, utf8 } = CYZ;
  const make = kind => {
    let seed = 7; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
    if (kind === 'text') return utf8('Security is a process, not a product. Attackers look for the weakest link, so defenders must think in layers. '.repeat(12)).slice(0, 1024);
    if (kind === 'code') { const ops = [0x55, 0x48, 0x89, 0xe5, 0x8b, 0x45, 0xfc, 0x83, 0xc0, 0x01, 0xc3, 0x00, 0x00, 0xe8, 0x0f, 0x1f]; return Array.from({ length: 1024 }, () => ops[Math.floor(rnd() * rnd() * 16)]); }
    return Array.from({ length: 1024 }, () => Math.floor(rnd() * 256));
  };
  const H = a => { const c = new Array(256).fill(0); a.forEach(b => c[b]++); return -c.filter(Boolean).reduce((s, k) => s + k / a.length * Math.log2(k / a.length), 0); };
  trace('cyentropy', {
    title: 'Entropy: does this file look packed or encrypted?',
    sub: 'Shannon entropy H = −Σ p·log₂ p measures how evenly the 256 byte values are used. Text and normal code use few values often (low H). Compressed, packed or encrypted data uses all values almost equally (H near 8 bits per byte).',
    W: 600, H: 340,
    params: [
      { k: 'kind', label: 'Sample (1024 bytes)', type: 'select', v: 'text', opts: [['text', 'English text'], ['code', 'Machine code section'], ['enc', 'Encrypted or packed section']] }
    ],
    tips: [
      { t: 'Play English text. A few letters and the space dominate, so entropy is around 4 bits per byte.', play: true },
      { t: 'Choose an encrypted section. The histogram is flat and entropy is close to 8, which is why packers and ransomware stand out.', set: { kind: 'enc' }, play: true }
    ],
    frames(p) {
      const data = make(p.kind), c = new Array(16).fill(0); data.forEach(b => c[b >> 4]++);
      const e = H(data);
      const fr = [
        { st: 1, data, c, say: `The first bytes: ${data.slice(0, 12).map(b => b.toString(16).padStart(2, '0')).join(' ')} ... 1024 bytes in all.` },
        { st: 2, data, c, say: 'Count how often each byte value appears. The chart groups the 256 values into 16 bins of 16 values each.' },
        { st: 3, data, c, e, say: `H = &minus;&Sigma; p<sub>i</sub> log<sub>2</sub> p<sub>i</sub> over all 256 values = <b>${e.toFixed(2)}</b> bits per byte. The maximum is 8, when every value has p = 1/256.` },
        { st: 4, done: true, data, c, e, say: e > 7.2 ? 'Near 8: compressed, packed or encrypted. Malware packers hide code this way, and a burst of files rewritten at this entropy suggests ransomware. JPEG, ZIP and video are also high, so tools combine entropy with other signals.' : 'Well below 8: structured data. A section of a program that suddenly jumps to near 8 is a classic sign of a packer.' }
      ];
      return fr.map(x => ({ ...x, kind: p.kind }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, L = 40, B = 250, W = 360, Hh = 200, mx = Math.max(...f.c);
      if (f.st >= 2) {
        D.line(g, L, B, L + W, B, col.line, 1.5);
        f.c.forEach((v, i) => { const h = v / mx * Hh; D.rect(g, L + i * (W / 16) + 2, B - h, W / 16 - 4, h, { fill: f.st >= 3 && f.e > 7.2 ? col.red : col.cv }); D.text(g, (i * 16).toString(16), L + i * (W / 16) + W / 32, B + 13, { a: 'center', s: 9, c: col.ink2 }); });
        D.text(g, 'byte value bins (hex)', L + W / 2, B + 28, { a: 'center', s: 10, b: true, c: col.ink2 });
      } else {
        for (let i = 0; i < 48; i++) cbox(z, 14 + (i % 12) * 48, 30 + Math.floor(i / 12) * 34, 44, 28, f.data[i].toString(16).padStart(2, '0'), { s: 12, b: true, mono: true, fill: col.surf });
      }
      if (f.st >= 3) {
        cbox(z, 430, 30, 156, 60, ['entropy', `${f.e.toFixed(2)} / 8`], { s: 15, b: true, fill: f.e > 7.2 ? 'rgba(225,29,72,0.2)' : 'rgba(15,118,110,0.2)' });
        D.rect(g, 430, 104, 156, 16, { fill: col.bg, stroke: col.line }); D.rect(g, 430, 104, 156 * f.e / 8, 16, { fill: f.e > 7.2 ? col.red : col.cv });
      }
      if (f.done) cbox(z, 14, 306, 572, 28, f.e > 7.2 ? 'high entropy: packed, compressed or encrypted' : 'low entropy: normal structured data', { s: 13, b: true, fill: f.e > 7.2 ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 3.1  A YARA style scan: strings, a condition, and a hash list, file by file
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const FILES = [
    ['readme.txt', 'Thanks for installing. Docs at example.org', []],
    ['HOW_TO_RECOVER.txt', 'Your files have been encrypted. Pay in Bitcoin at abc.onion', ['$a', '$b', '$c']],
    ['crypto_news.html', 'Bitcoin price rises again', ['$b']],
    ['notes.txt', 'Read the .onion guide and buy bitcoin safely', ['$b', '$c']]
  ];
  trace('cyyara', {
    title: 'Signature scanning: a YARA style rule',
    sub: 'A rule names byte strings and a condition. The scanner checks each file and reports a match when the condition holds. Changing the condition trades missed detections for false alarms.',
    W: 600, H: 340,
    params: [
      { k: 'need', label: 'Condition', type: 'select', v: '2', opts: [['1', 'any of them'], ['2', '2 of them'], ['3', 'all of them']] }
    ],
    tips: [
      { t: 'Play "2 of them". The ransom note matches, but so does an innocent notes file that mentions bitcoin and .onion: a false positive.', play: true },
      { t: 'Choose "all of them". Only the ransom note matches. Stricter rules miss variants that change one string.', set: { need: '3' }, play: true },
      { t: 'Choose "any of them". Even the crypto news page matches. Loose rules flood analysts.', set: { need: '1' }, play: true }
    ],
    frames(p) {
      const need = +p.need, rows = [];
      const fr = [{ st: 0, rows: [], say: `Rule Toy_Ransom_Note: $a = "files have been encrypted", $b = "bitcoin", $c = ".onion" (case ignored). Condition: ${need === 1 ? 'any of them' : need === 3 ? 'all of them' : '2 of them'}.` }];
      FILES.forEach(([name, text, hits]) => {
        const m = hits.length >= need, bad = name === 'HOW_TO_RECOVER.txt';
        rows.push({ name, hits, m, bad });
        fr.push({ st: 1, rows: rows.slice(), say: `${name}: found ${hits.length ? hits.join(', ') : 'nothing'}. ${m ? (bad ? '<b>Match</b>, and it really is a ransom note.' : '<b>Match</b>, but this file is harmless: a false positive.') : (bad ? 'No match: a missed detection.' : 'No match.')}` });
      });
      const fp = rows.filter(r => r.m && !r.bad).length;
      fr.push({ st: 2, done: true, rows, fp, say: `${fp} false positive${fp === 1 ? '' : 's'}. Real rules combine distinctive strings, byte patterns, file size and structure (for example the file must start with MZ) to stay precise, and they are tested against large sets of clean files before use.` });
      return fr.map(x => ({ ...x, need }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      ['$a encrypted', '$b bitcoin', '$c .onion'].forEach((t, i) => cbox(z, 14 + i * 150, 12, 140, 26, t, { s: 11, b: true, mono: true, fill: col.surf }));
      cbox(z, 470, 12, 116, 26, `need ${f.need}`, { s: 12, b: true, fill: col.bg });
      f.rows.forEach((r, i) => {
        const y = 52 + i * 60;
        cbox(z, 14, y, 190, 48, r.name, { s: 12, b: true, mono: true, fill: col.surf });
        ['$a', '$b', '$c'].forEach((s, j) => cbox(z, 214 + j * 64, y + 8, 56, 32, s, { s: 12, b: true, mono: true, fill: r.hits.includes(s) ? col.cv : col.bg, c: r.hits.includes(s) ? '#fff' : col.ink2 }));
        cbox(z, 410, y + 4, 176, 40, r.m ? (r.bad ? 'match (true)' : 'match (false alarm)') : (r.bad ? 'missed' : 'clean'), { s: 12, b: true, fill: r.m ? (r.bad ? col.red : col.orange) : r.bad ? col.ink2 : col.green, c: '#fff' });
      });
      if (f.done) cbox(z, 14, 306, 572, 28, f.fp ? `${f.fp} false alarm(s): rule too loose` : 'precise: only the ransom note matched', { s: 13, b: true, fill: f.fp ? col.orange : col.cv, c: '#fff' });
    }
  });
})();
