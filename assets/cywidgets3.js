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
