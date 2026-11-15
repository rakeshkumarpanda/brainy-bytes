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
