/* ===== More interactive widgets for the Manual Testing lessons (built by tools/mt-build) ===== */
(() => {
  const K = VIZ.kit, W = VIZ.widgets, esc = K.esc, $ = K.$;
  const X = () => (typeof PAGE !== 'undefined' && PAGE.x) || {};
  const pct = (a, b) => (b ? (a * 100 / b) : 0);
  const f1 = n => (Math.round(n * 10) / 10).toLocaleString('en-US');
  const f2 = n => (Math.round(n * 100) / 100).toLocaleString('en-US');

  /* ----- spot the unclear words in a requirement ----- */
  W.ambiguity = el => {
    const spec = (X().amb || {})[el.dataset.k];
    if (!spec) { el.textContent = 'Missing requirement ' + el.dataset.k; return; }
    const b = K.shell(el, spec.t, 'Read the requirement like a reviewer. Tap every word or phrase that a developer and a tester could understand differently.');
    const parts = [];
    spec.req.replace(/\[\[([^|\]]+)\|([^\]]+)\]\]|([^\[]+)/g, (m, w, why, plain) => { parts.push(w ? { w, why } : { plain }); return m; });
    const total = parts.filter(p => p.w).length;
    let found = new Set();
    b.innerHTML = `<div class="m2-req"></div><div class="vz-row"><span class="m2-score"></span><button type="button" class="vz-next" data-a="all">Show all</button><button type="button" class="vz-next" data-a="reset">Start again</button></div><div class="vz-msg" aria-live="polite">Tap a word.</div><div class="m2-fix" hidden><b>✍️ The same requirement, rewritten so it can be tested:</b><p></p></div>`;
    const draw = () => {
      $('.m2-req', b).innerHTML = parts.map((p, i) => p.w
        ? `<button type="button" class="m2-w${found.has(i) ? ' hit' : ''}" data-i="${i}">${esc(p.w)}</button>`
        : p.plain.split(/(\s+)/).map(t => t.trim() ? `<span class="m2-p">${esc(t)}</span>` : t).join('')).join('');
      $('.m2-score', b).innerHTML = `Found <b>${found.size}</b> of <b>${total}</b> unclear phrases`;
      const fx = $('.m2-fix', b);
      fx.hidden = found.size < total;
      $('p', fx).textContent = spec.fix;
    };
    b.addEventListener('click', e => {
      const w = e.target.closest('.m2-w'), p = e.target.closest('.m2-p'), a = e.target.closest('[data-a]');
      const msg = $('.vz-msg', b);
      if (w) {
        const i = +w.dataset.i; found.add(i); draw();
        msg.innerHTML = `<b>"${esc(parts[i].w)}"</b>: ${esc(parts[i].why)}`;
      } else if (p) {
        msg.innerHTML = `<b>"${esc(p.textContent)}"</b> is clear enough. Keep looking.`;
      } else if (a && a.dataset.a === 'all') {
        parts.forEach((x, i) => x.w && found.add(i)); draw();
        msg.innerHTML = 'Every unclear phrase is marked. Each one becomes a question for the business analyst in the review meeting.';
      } else if (a) { found = new Set(); draw(); msg.innerHTML = 'Tap a word.'; }
    });
    draw();
  };

  /* ----- the test pyramid against the ice cream cone ----- */
  W.pyramid = el => {
    const b = K.shell(el, 'Test pyramid or ice cream cone', 'Pick a shape, then change how many tests sit in each layer. Watch how long one full run takes and how many runs fail for no real reason.');
    const L = [['ui', '🖥️ UI and end to end', 45, 0.5], ['api', '🔌 API and service', 1.5, 0.02], ['unit', '🧱 Unit', 0.02, 0.0005]];
    const SH = { pyr: [20, 120, 900], cone: [400, 60, 30] };
    let n = SH.pyr.slice();
    b.innerHTML = `<div class="vz-row">${K.seg('sh', [['pyr', '🔺 Healthy pyramid'], ['cone', '🍦 Ice cream cone']], 'pyr')}</div><div class="m2-sls"></div><div class="m2-pyr"></div><div class="m2-stats"></div><div class="vz-msg" aria-live="polite"></div>`;
    const sl = () => {
      $('.m2-sls', b).innerHTML = L.map(([k, l], i) => K.slider(k, l, 0, i === 2 ? 1500 : 600, n[i], 10)).join('');
      L.forEach(([k], i) => K.wireSlider(b, k, v => { n[i] = v; draw(); }));
    };
    const draw = () => {
      const mx = Math.max(...n, 1);
      $('.m2-pyr', b).innerHTML = L.map(([k, l], i) => `<div class="m2-layer m2-${k}" style="width:${Math.max(14, n[i] * 100 / mx)}%"><span>${l.split(' ').slice(1).join(' ')}: <b>${n[i]}</b></span></div>`).join('');
      const secs = n.reduce((s, c, i) => s + c * L[i][2], 0);
      const pPass = n.reduce((p, c, i) => p * Math.pow(1 - L[i][3] / 100, c), 1);
      const mins = secs / 60;
      $('.m2-stats', b).innerHTML = `<div class="m2-stat"><small>One full run takes</small><b>${mins >= 60 ? f1(mins / 60) + ' h' : f1(mins) + ' min'}</b></div><div class="m2-stat"><small>Runs that fail with no real bug</small><b>${f1((1 - pPass) * 100)}%</b></div><div class="m2-stat"><small>Total tests</small><b>${n.reduce((a, c) => a + c, 0).toLocaleString('en-US')}</b></div>`;
      const top = n[0] > n[2];
      $('.vz-msg', b).innerHTML = top
        ? '<b>Top heavy.</b> Most checks go through the screen. They are slow and break when a button moves, so the team stops trusting the results. Push checks down to the API and unit layers.'
        : '<b>Healthy shape.</b> Many small fast checks at the bottom, fewer at the top. A run finishes during a coffee break, and a red result usually means a real bug.';
    };
    K.wireSeg(b, 'sh', v => { n = SH[v].slice(); sl(); draw(); });
    sl(); draw();
  };

  /* ----- a canary release, stage by stage ----- */
  W.canary = el => {
    const b = K.shell(el, 'Roll out a new build to a few users first', 'Set how buggy the new build secretly is, then move it to more users one stage at a time. The monitor rolls it back when errors cross 1%.');
    const ST = [1, 5, 25, 50, 100], USERS = 200000;
    let stage = -1, rate = 0.4, dead = false;
    b.innerHTML = `<div class="vz-row">${K.slider('r', 'Hidden error rate of the new build (%)', 0, 6, rate, 0.2)}</div>
      <div class="m2-stages">${ST.map((s, i) => `<span class="m2-stg" data-i="${i}">${s}%</span>`).join('')}</div>
      <div class="m2-split"><i class="m2-old"></i><i class="m2-new"></i></div>
      <div class="m2-stats"></div>
      <div class="vz-row"><button type="button" class="vz-next" data-a="go">▶ Next stage</button><button type="button" class="vz-next" data-a="reset">↺ Start again</button></div>
      <div class="vz-msg" aria-live="polite">Version 1 serves everyone. Press Next stage to send 1% of users to version 2.</div>`;
    const draw = () => {
      const p = stage < 0 || dead ? 0 : ST[stage];
      $('.m2-old', b).style.width = (100 - p) + '%';
      $('.m2-new', b).style.width = p + '%';
      b.querySelectorAll('.m2-stg').forEach((x, i) => { x.classList.toggle('on', i <= stage && !dead); x.classList.toggle('bad', dead && i === stage); });
      const users = USERS * p / 100, errs = users * rate / 100;
      $('.m2-stats', b).innerHTML = `<div class="m2-stat"><small>Users on version 2</small><b>${Math.round(users).toLocaleString('en-US')}</b></div><div class="m2-stat"><small>Users who hit an error</small><b>${Math.round(errs).toLocaleString('en-US')}</b></div><div class="m2-stat"><small>Error rate seen by the monitor</small><b>${p ? f1(rate) : 0}%</b></div>`;
    };
    K.wireSlider(b, 'r', v => { rate = v; draw(); });
    b.addEventListener('click', e => {
      const a = e.target.closest('[data-a]'); if (!a) return;
      const msg = $('.vz-msg', b);
      if (a.dataset.a === 'reset') { stage = -1; dead = false; draw(); msg.innerHTML = 'Version 1 serves everyone. Press Next stage to send 1% of users to version 2.'; return; }
      if (dead || stage === ST.length - 1) return;
      stage++;
      const hurt = Math.round(USERS * ST[stage] / 100 * rate / 100);
      if (rate > 1) {
        dead = true; draw();
        msg.innerHTML = `<b>🚨 Rolled back at ${ST[stage]}%.</b> The monitor saw ${f1(rate)}% errors, above the 1% limit, and moved everyone back to version 1. Only ${hurt.toLocaleString('en-US')} users met the bug, instead of ${Math.round(USERS * rate / 100).toLocaleString('en-US')} with a big bang release. Now a bug report is raised with the logs from those sessions.`;
      } else {
        draw();
        msg.innerHTML = stage === ST.length - 1
          ? `<b>✅ Fully released.</b> Every stage stayed under the 1% limit, so version 2 now serves all users.`
          : `<b>Stage ${stage + 1}: ${ST[stage]}% of users.</b> Error rate ${f1(rate)}% is under the 1% limit, so the release may continue. ${hurt ? hurt.toLocaleString('en-US') + ' users still met small errors, which the team reviews.' : ''}`;
      }
    });
    draw();
  };

  /* ----- colour contrast checker (WCAG) ----- */
  W.contrast = el => {
    const b = K.shell(el, 'Check a colour pair yourself', 'Pick a text colour and a background colour, or load a pair. The ratio is worked out with the formula from the WCAG guidelines.');
    const PRE = [['#767676', '#ffffff', 'Grey on white'], ['#999999', '#ffffff', 'Light grey on white'], ['#ffffff', '#2b7de9', 'White on blue'], ['#ffd400', '#ffffff', 'Yellow on white'], ['#1a1a1a', '#ffc928', 'Black on yellow']];
    b.innerHTML = `<div class="vz-row"><label class="m2-col">Text <input type="color" data-c="fg" value="#767676"></label><label class="m2-col">Background <input type="color" data-c="bg" value="#ffffff"></label></div>
      <div class="vz-ops">${PRE.map((p, i) => `<button type="button" data-p="${i}">${p[2]}</button>`).join('')}</div>
      <div class="m2-sample"><p class="m2-s1">Pay ₹499 now</p><p class="m2-s2">Small print: refunds take 5 to 7 working days.</p></div>
      <div class="m2-ratio"></div><div class="m2-checks"></div>`;
    const lum = hex => {
      const c = [1, 3, 5].map(i => parseInt(hex.substr(i, 2), 16) / 255).map(v => v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
      return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
    };
    const draw = () => {
      const fg = $('[data-c="fg"]', b).value, bg = $('[data-c="bg"]', b).value;
      const s = $('.m2-sample', b); s.style.color = fg; s.style.background = bg;
      const L1 = lum(fg), L2 = lum(bg), r = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
      $('.m2-ratio', b).innerHTML = `Contrast ratio <b>${f2(r)} : 1</b> <small>(L1 + 0.05) ÷ (L2 + 0.05) = (${f2(Math.max(L1, L2))} + 0.05) ÷ (${f2(Math.min(L1, L2))} + 0.05)</small>`;
      const C = [['Normal text, level AA', 4.5], ['Large text, level AA', 3], ['Buttons, icons and borders (AA)', 3], ['Normal text, level AAA', 7], ['Large text, level AAA', 4.5]];
      $('.m2-checks', b).innerHTML = C.map(([l, n]) => `<div class="eg-r ${r >= n ? 'ok' : 'bad'}"><span>${r >= n ? '✓' : '✗'} ${l}</span><b>${n} : 1</b><small>${r >= n ? 'passes' : 'fails'}</small></div>`).join('');
    };
    b.addEventListener('input', draw);
    b.addEventListener('click', e => {
      const p = e.target.closest('[data-p]'); if (!p) return;
      const [fg, bg] = PRE[+p.dataset.p];
      $('[data-c="fg"]', b).value = fg; $('[data-c="bg"]', b).value = bg; draw();
    });
    draw();
  };

  /* ----- the same screen in many countries ----- */
  W.locale = el => {
    const b = K.shell(el, 'One checkout, many countries', 'Choose a country and type an amount and a date. The browser formats them the way people there expect, which is exactly what a localization tester checks.');
    const LOC = {
      'en-US': ['🇺🇸 United States', 'USD', 'Pay now'], 'en-IN': ['🇮🇳 India', 'INR', 'Pay now'], 'hi-IN': ['🇮🇳 India, Hindi', 'INR', 'अभी भुगतान करें'],
      'de-DE': ['🇩🇪 Germany', 'EUR', 'Jetzt bezahlen'], 'fr-FR': ['🇫🇷 France', 'EUR', 'Payer maintenant'], 'ar-EG': ['🇪🇬 Egypt, Arabic', 'EGP', 'ادفع الآن'],
      'ja-JP': ['🇯🇵 Japan', 'JPY', '今すぐ支払う'], 'en-GB': ['🇬🇧 United Kingdom', 'GBP', 'Pay now']
    };
    b.innerHTML = `<div class="vz-row"><label class="m2-col">Country <select data-l>${Object.entries(LOC).map(([k, v]) => `<option value="${k}">${v[0]}</option>`).join('')}</select></label>
      <label class="m2-col">Amount <input type="number" data-a value="1234567.5" step="0.01"></label><label class="m2-col">Date <input type="date" data-d value="2026-03-04"></label></div>
      <div class="m2-shop"></div><div class="vz-msg" aria-live="polite"></div>`;
    $('[data-l]', b).value = 'en-IN';
    const draw = () => {
      const l = $('[data-l]', b).value, [, cur, pay] = LOC[l];
      const amt = parseFloat($('[data-a]', b).value) || 0;
      const d = new Date(($('[data-d]', b).value || '2026-03-04') + 'T12:00:00');
      let money, num, ds, dl;
      try {
        money = new Intl.NumberFormat(l, { style: 'currency', currency: cur }).format(amt);
        num = new Intl.NumberFormat(l).format(amt);
        ds = new Intl.DateTimeFormat(l, { dateStyle: 'short' }).format(d);
        dl = new Intl.DateTimeFormat(l, { dateStyle: 'full' }).format(d);
      } catch (e) { money = num = ds = dl = String(amt); }
      const rtl = l.startsWith('ar');
      const grow = Math.round((pay.length / 'Pay now'.length - 1) * 100);
      $('.m2-shop', b).innerHTML = `<div class="m2-card" dir="${rtl ? 'rtl' : 'ltr'}" lang="${l}"><div class="m2-cl"><small>Total</small><b>${esc(money)}</b></div><div class="m2-cl"><small>Delivery</small><b>${esc(dl)}</b></div><button type="button" class="m2-pay">${esc(pay)}</button></div>
        <div class="tw"><table class="jt"><tr><th>What</th><th>Shown as</th></tr><tr><td>Plain number</td><td>${esc(num)}</td></tr><tr><td>Short date</td><td>${esc(ds)}</td></tr><tr><td>Text direction</td><td>${rtl ? 'Right to left' : 'Left to right'}</td></tr><tr><td>Button text length</td><td>${pay.length} characters (${grow >= 0 ? '+' : ''}${grow}% against English)</td></tr></table></div>`;
      $('.vz-msg', b).innerHTML = rtl
        ? '<b>Right to left.</b> The whole layout flips: the total moves to the right and icons that point forward must point the other way. A tester checks that nothing overlaps and the order still makes sense.'
        : (grow > 40 ? `<b>Text grows by ${grow}%.</b> A button sized for "Pay now" may cut this text or wrap it onto two lines. Testers check every button and label in the longest language.`
          : 'Look at the separators. One country writes a decimal point, another a comma, and India groups digits in lakhs. A date like 04/03 means 4 March in one country and 3 April in another.');
    };
    b.addEventListener('input', draw);
    b.addEventListener('change', draw);
    draw();
  };

  /* ----- three point estimation ----- */
  W.estimate = el => {
    const b = K.shell(el, 'Estimate with three numbers', 'Pick a task and give its best case, most likely and worst case in days. The total shows a range, not a single promise.');
    const T = (X().est && X().est.tasks) || [['Design test cases', 3, 5, 10], ['Prepare test data', 1, 2, 6], ['Execution, cycle 1', 4, 6, 12], ['Retest and regression', 2, 4, 9]];
    let sel = 0;
    b.innerHTML = `<div class="vz-row">${K.seg('t', T.map((t, i) => [i, t[0]]), 0)}</div><div class="m2-sls"></div><div class="m2-est"></div><div class="vz-msg" aria-live="polite"></div>`;
    const sl = () => {
      const t = T[sel];
      $('.m2-sls', b).innerHTML = K.slider('o', '😀 Best case', 1, 30, t[1]) + K.slider('m', '🙂 Most likely', 1, 30, t[2]) + K.slider('p', '😟 Worst case', 1, 40, t[3]);
      ['o', 'm', 'p'].forEach((k, j) => K.wireSlider(b, k, v => { T[sel][j + 1] = v; draw(); }));
    };
    const draw = () => {
      let E = 0, V = 0;
      const rows = T.map(([n, o, m, p]) => {
        const lo = Math.min(o, m, p), hi = Math.max(o, m, p);
        const e = (o + 4 * m + p) / 6, sd = (hi - lo) / 6;
        E += e; V += sd * sd;
        return `<tr><td>${esc(n)}</td><td>${o}, ${m}, ${p}</td><td>(${o} + 4 × ${m} + ${p}) ÷ 6 = <b>${f1(e)}</b></td><td>${f2(sd)}</td></tr>`;
      }).join('');
      const SD = Math.sqrt(V);
      $('.m2-est', b).innerHTML = `<div class="tw"><table class="jt"><tr><th>Task</th><th>Best, likely, worst</th><th>Expected E</th><th>Spread SD</th></tr>${rows}<tr><td><b>Total</b></td><td></td><td><b>${f1(E)} days</b></td><td>${f2(SD)}</td></tr></table></div>`;
      $('.vz-msg', b).innerHTML = `Tell the manager: <b>about ${f1(E)} days</b>, and very likely between <b>${f1(Math.max(0, E - 2 * SD))}</b> and <b>${f1(E + 2 * SD)}</b> days (E ± 2 SD). A wide range means the work is uncertain, so split it or remove the unknowns first.`;
    };
    K.wireSeg(b, 't', v => { sel = +v; sl(); });
    sl(); draw();
  };

  /* ----- test and defect metrics calculator ----- */
  W.metrics = el => {
    const b = K.shell(el, 'Work out the numbers of a release', 'Change any count. Every metric updates with its formula, so you can see where each number comes from.');
    const F = [['plan', 'Test cases planned', 400], ['exec', 'Test cases executed', 380], ['pass', 'Test cases passed', 342], ['found', 'Defects found by the test team', 90], ['rej', 'Of those, rejected as invalid', 9], ['leak', 'Defects found by users after release', 10], ['kloc', 'Size of the code in KLOC', 45]];
    b.innerHTML = `<div class="m2-inputs">${F.map(([k, l, v]) => `<label class="m2-num">${l}<input type="number" min="0" data-f="${k}" value="${v}"></label>`).join('')}</div><div class="m2-mt"></div>`;
    const draw = () => {
      const v = {}; F.forEach(([k]) => { v[k] = Math.max(0, +$(`[data-f="${k}"]`, b).value || 0); });
      const valid = v.found - v.rej;
      const M = [
        ['Execution progress', 'executed × 100 ÷ planned', pct(v.exec, v.plan), '%', 'How much of the plan has been run.'],
        ['Pass rate', 'passed × 100 ÷ executed', pct(v.pass, v.exec), '%', 'How much of what ran is working.'],
        ['Defect rejection ratio', 'rejected × 100 ÷ found', pct(v.rej, v.found), '%', 'High values mean unclear requirements or weak bug reports.'],
        ['Defect removal efficiency (DRE)', 'valid found × 100 ÷ (valid found + found by users)', pct(valid, valid + v.leak), '%', 'Above 90% is usually a good team. 100% would mean users found nothing.'],
        ['Defect leakage', 'found by users × 100 ÷ (valid found + found by users)', pct(v.leak, valid + v.leak), '%', 'The share of bugs that escaped testing.'],
        ['Defect density', 'valid defects ÷ KLOC', v.kloc ? (valid + v.leak) / v.kloc : 0, ' per KLOC', 'Compare modules. The densest module gets more testing next time.']];
      $('.m2-mt', b).innerHTML = M.map(([n, f, x, u, why]) => `<div class="m2-m"><div><b>${n}</b><small>${f}</small></div><span>${f1(x)}${u}</span><p>${why}</p></div>`).join('');
    };
    b.addEventListener('input', draw);
    draw();
  };

  /* ----- testing an AI chatbot: which oracle can you trust ----- */
  W.aioracle = el => {
    const b = K.shell(el, 'Test a chatbot that never answers the same way twice', 'The policy says: a damaged item can be refunded within 30 days if the customer sends a photo. Ask the bot again and again, then compare three ways of judging its answers.');
    const A = [
      ['You can return a damaged item within 30 days. Please attach a photo.', true],
      ['Damaged items can be refunded within thirty days if you share a picture of the damage.', true],
      ['Sure! Our refund window is 30 days, and a photo of the damage is needed.', true],
      ['You have 60 days to return damaged items. A photo helps.', false],
      ['Refunds for damaged goods are accepted within 30 days, no proof needed.', false],
      ['It is not 30 days and no photo is needed. You get 90 days.', false],
      ['Within 30 days, with a photo of the damaged item, you get a full refund.', true]];
    const EXP = A[0][0];
    const kw = t => /\b(30|thirty)\b/i.test(t) && /(photo|picture)/i.test(t);
    const rub = t => /\b(30|thirty)\b/i.test(t) && /(photo|picture)/i.test(t) && !/(60|90|not 30|no (proof|photo))/i.test(t);
    const O = [['exact', 'Exact text match', t => t === EXP], ['kw', 'Contains key words', kw], ['rub', 'Rubric of facts', rub]];
    let runs = [], bag = [];
    b.innerHTML = `<div class="vz-row"><button type="button" class="vz-next" data-a="ask">💬 Ask the bot</button><button type="button" class="vz-next" data-a="ten">Ask 7 more times</button><button type="button" class="vz-next" data-a="reset">↺ Clear</button></div>
      <div class="vz-scroll"><div class="m2-runs"></div></div><div class="m2-stats"></div><div class="vz-msg" aria-live="polite">Question: "Can I get a refund for a damaged item?" Press Ask the bot.</div>`;
    const ask = () => { if (!bag.length) bag = A.map((_, i) => i).sort(() => Math.random() - 0.5); runs.push(bag.pop()); };
    const draw = () => {
      $('.m2-runs', b).innerHTML = runs.length ? `<table class="jt"><tr><th>#</th><th>Bot answer</th><th>Really correct</th>${O.map(o => `<th>${o[1]}</th>`).join('')}</tr>${runs.map((r, i) => {
        const [t, ok] = A[r];
        return `<tr><td>${i + 1}</td><td>${esc(t)}</td><td class="${ok ? 'yes' : 'no'}">${ok ? 'Yes' : 'No'}</td>${O.map(o => { const v = o[2](t); return `<td class="${v === ok ? 'yes' : 'no'}">${v ? 'Pass' : 'Fail'}${v === ok ? '' : ' ⚠️'}</td>`; }).join('')}</tr>`;
      }).join('')}</table>` : '';
      const wrong = O.map(o => runs.filter(r => o[2](A[r][0]) !== A[r][1]).length);
      $('.m2-stats', b).innerHTML = runs.length ? O.map((o, i) => `<div class="m2-stat"><small>${o[1]}: wrong verdicts</small><b>${wrong[i]} of ${runs.length}</b></div>`).join('') : '';
      if (runs.length > 2) $('.vz-msg', b).innerHTML = '<b>What this shows.</b> An exact match fails good answers that use other words, so it raises false alarms. Key words pass answers that mention 30 and photo but say something wrong. A rubric checks each fact and catches contradictions. Real teams also ask a person, or a second model, to grade a sample of answers.';
    };
    b.addEventListener('click', e => {
      const a = e.target.closest('[data-a]'); if (!a) return;
      if (a.dataset.a === 'ask') ask();
      else if (a.dataset.a === 'ten') for (let i = 0; i < 7; i++) ask();
      else { runs = []; bag = []; $('.vz-msg', b).innerHTML = 'Question: "Can I get a refund for a damaged item?" Press Ask the bot.'; }
      draw();
    });
    draw();
  };

  /* ----- what a screen reader announces ----- */
  W.srsim = el => {
    const b = K.shell(el, 'Hear the page the way a blind user does', 'Press Tab to move through the page like a keyboard user. The box on the right shows what the screen reader says. Then switch to the fixed version.');
    const V = {
      bad: [['🛍️', 'logo.png', '"Image. logo dot png."', 'The image has no text alternative, so the file name is read out. WCAG 1.1.1 Non-text content.'],
        ['✉️', '[ ________ ]', '"Edit text."', 'The field has no label. The user does not know what to type. WCAG 1.3.1 and 3.3.2 Labels.'],
        ['🔗', 'Click here', '"Link. Click here."', 'Out of context the link means nothing. WCAG 2.4.4 Link purpose.'],
        ['💳', 'Pay ₹499 (a styled div)', '(nothing, it is skipped)', 'The pay "button" is a plain box that the keyboard cannot reach. Keyboard users cannot buy at all. WCAG 2.1.1 Keyboard.']],
      good: [['🛍️', 'Brainy Shop logo', '"Brainy Shop, home. Link, image."', 'The image has alt text that says where it leads.'],
        ['✉️', 'Email address [ ________ ]', '"Email address, required. Edit text."', 'The label is tied to the field, so it is announced.'],
        ['🔗', 'Read the refund policy', '"Link. Read the refund policy."', 'The link text makes sense on its own.'],
        ['💳', 'Pay ₹499', '"Pay 499 rupees. Button."', 'A real button: it gets keyboard focus, and Enter or Space presses it.']]
    };
    let v = 'bad', at = -1;
    b.innerHTML = `<div class="vz-row">${K.seg('v', [['bad', '😕 Before the fix'], ['good', '😊 After the fix']], 'bad')}<button type="button" class="vz-next" data-a="back">⇧ Tab</button><button type="button" class="vz-next" data-a="tab">Tab ⇥</button></div>
      <div class="m2-sr"><div class="m2-srpage"></div><div class="m2-srsay"><small>🔊 Screen reader says</small><b></b><p></p></div></div>`;
    const draw = () => {
      const items = V[v];
      const reach = v === 'bad' ? [0, 1, 2] : [0, 1, 2, 3];
      $('.m2-srpage', b).innerHTML = items.map((x, i) => `<div class="m2-sri${i === reach[at] ? ' on' : ''}${v === 'bad' && i === 3 ? ' dead' : ''}">${x[0]} ${esc(x[1])}</div>`).join('');
      const say = $('.m2-srsay', b);
      if (at < 0) { $('b', say).textContent = '(press Tab)'; $('p', say).textContent = ''; return; }
      if (at >= reach.length) {
        $('b', say).textContent = '"End of page."';
        $('p', say).textContent = v === 'bad' ? 'Focus never reached the Pay button. That is a blocker for a keyboard or screen reader user.' : 'Every control was reached and announced with its name and role.';
        return;
      }
      const x = items[reach[at]];
      $('b', say).textContent = x[2]; $('p', say).textContent = x[3];
    };
    K.wireSeg(b, 'v', x => { v = x; at = -1; draw(); });
    b.addEventListener('click', e => {
      const a = e.target.closest('[data-a]'); if (!a) return;
      const max = v === 'bad' ? 3 : 4;
      at = a.dataset.a === 'tab' ? Math.min(max, at + 1) : Math.max(-1, at - 1);
      draw();
    });
    draw();
  };

  /* ----- a flaky test ----- */
  W.flaky = el => {
    const b = K.shell(el, 'Run a flaky test twenty times', 'Set how often the test fails for no real reason, then run it. Turn on automatic retry and see what it hides.');
    let p = 10, retry = false, res = [];
    b.innerHTML = `<div class="vz-row">${K.slider('p', 'Random failure chance (%)', 0, 40, p)}${K.seg('r', [['0', 'No retry'], ['1', 'Retry once']], '0')}<button type="button" class="vz-next" data-a="run">▶ Run 20 times</button></div>
      <div class="m2-strip"></div><div class="m2-stats"></div><div class="vz-msg" aria-live="polite">Press Run 20 times.</div>`;
    const draw = () => {
      $('.m2-strip', b).innerHTML = res.map(r => `<i class="${r === 2 ? 'warn' : r ? 'ok' : 'bad'}" title="${r === 2 ? 'failed, then passed on retry' : r ? 'passed' : 'failed'}"></i>`).join('');
      const fails = res.filter(r => r === 0).length, hidden = res.filter(r => r === 2).length;
      const allGreen = Math.pow(1 - p / 100, 20) * 100;
      $('.m2-stats', b).innerHTML = `<div class="m2-stat"><small>Red runs</small><b>${fails}</b></div><div class="m2-stat"><small>Failures hidden by retry</small><b>${hidden}</b></div><div class="m2-stat"><small>Chance that 20 runs are all green</small><b>${f1(allGreen)}%</b></div>`;
    };
    K.wireSlider(b, 'p', v => { p = v; draw(); });
    K.wireSeg(b, 'r', v => { retry = v === '1'; });
    b.addEventListener('click', e => {
      if (!e.target.closest('[data-a="run"]')) return;
      res = [];
      for (let i = 0; i < 20; i++) {
        const ok = Math.random() >= p / 100;
        res.push(ok ? 1 : (retry && Math.random() >= p / 100 ? 2 : 0));
      }
      draw();
      const fails = res.filter(r => r === 0).length, hidden = res.filter(r => r === 2).length;
      $('.vz-msg', b).innerHTML = retry
        ? `<b>Retry turned ${hidden} red runs green.</b> The pipeline looks calm, but the test is still unreliable. If the cause is a real race condition in the product, users will meet it too. Report it as a flaky test with the failure logs.`
        : (fails ? `<b>${fails} of 20 runs failed</b> with no change to the code. People start to ignore red results, and then a real bug slips through. Put the test in quarantine, find the cause (timing, shared data, test order) and fix it.` : '<b>All green this time.</b> Run it again. A flaky test hides between runs.');
    });
    draw();
  };

  /* ----- interrupting a mobile app in the middle of a payment ----- */
  W.mobileint = el => {
    const b = K.shell(el, 'Interrupt a payment on a phone', 'A user is paying ₹499 in a shopping app. Pick something that happens to the phone at that exact moment and see what a tester checks.');
    const I = [['📞', 'Incoming call', 'The call screen covers the app. After the call the user returns to the payment screen with the same cart, and the payment is not charged twice.', 'The app restarts at the home page and the cart is empty, or the money is taken but no order is shown.'],
      ['📶', 'Network drops', 'The app shows a clear "You are offline" message, keeps the cart, and checks the payment status with the server when the network returns.', 'An endless spinner, or the user presses Pay again and is charged twice.'],
      ['🔋', 'Battery at 5%', 'The low battery pop up appears over the app. Closing it leaves the app exactly where it was.', 'The pop up steals focus and the Pay tap is lost without any message.'],
      ['🔄', 'Screen rotates', 'The layout turns to landscape and every typed value, such as the card number, stays in place.', 'The screen redraws and the form is empty, so the user has to type everything again.'],
      ['🏠', 'App sent to background for 10 minutes', 'Coming back, the session is still valid, or the app asks to log in again and then returns to the cart.', 'A crash on return, or an expired session that loses the order silently.'],
      ['🔔', 'Push notification', 'The banner shows on top and disappears. Tapping it opens the right screen, and the payment flow can be resumed.', 'Tapping the banner jumps away and the half finished payment is left in an unknown state.']];
    b.innerHTML = `<div class="m2-phonewrap"><div class="m2-phone"><div class="m2-scr"><b>🛒 Checkout</b><span>Total ₹499</span><span class="m2-paybtn">Paying…</span><div class="m2-over" hidden></div></div></div><div class="m2-pi"><div class="vz-ops">${I.map((x, i) => `<button type="button" data-i="${i}">${x[0]} ${x[1]}</button>`).join('')}</div><div class="vz-msg" aria-live="polite">Pick an interruption.</div></div></div>`;
    b.addEventListener('click', e => {
      const t = e.target.closest('[data-i]'); if (!t) return;
      const x = I[+t.dataset.i], ov = $('.m2-over', b);
      ov.hidden = false; ov.textContent = x[0]; ov.classList.remove('pop'); void ov.offsetWidth; ov.classList.add('pop');
      b.querySelectorAll('[data-i]').forEach(y => y.classList.toggle('on', y === t));
      $('.vz-msg', b).innerHTML = `<b>${x[0]} ${x[1]}</b><br>✅ <b>Expected:</b> ${x[2]}<br>🐞 <b>A common bug:</b> ${x[3]}`;
    });
  };

  /* ----- broken access control: change the id in the address ----- */
  W.idor = el => {
    const b = K.shell(el, 'Change one number in the address', 'You are logged in as Asha, customer 1042. Edit the number in the address bar and press Go. Then try the fixed build.');
    const NM = { 1040: 'Ravi K.', 1041: 'Meena P.', 1042: 'Asha R.', 1043: 'John D.', 1044: 'Fatima S.' };
    let build = 'bad';
    b.innerHTML = `<div class="vz-row">${K.seg('b', [['bad', '🐞 Build 7 (buggy)'], ['good', '🛡️ Build 8 (fixed)']], 'bad')}</div>
      <div class="m2-browser"><div class="m2-bar"><span>https://bank.example/accounts/</span><input data-id value="1042" inputmode="numeric" aria-label="Account number in the address"><span>/statement</span><button type="button" class="vz-next" data-a="go">Go</button></div><div class="m2-page"></div></div>
      <div class="vz-ops">${[1041, 1043, 1044, 'abc'].map(x => `<button type="button" data-t="${x}">try ${x}</button>`).join('')}</div>
      <div class="vz-msg" aria-live="polite"></div>`;
    const go = () => {
      const id = $('[data-id]', b).value.trim(), page = $('.m2-page', b), msg = $('.vz-msg', b);
      page.className = 'm2-page';
      if (!/^\d+$/.test(id) || !NM[id]) { page.innerHTML = '<b>404</b> No such account.'; msg.innerHTML = 'A friendly error with no details about the system. That is correct behaviour.'; return; }
      if (id === '1042') { page.innerHTML = `<b>Statement of ${NM[id]}</b><br>Balance ₹ 52,310 · last transfer ₹ 1,500 to Ravi`; msg.innerHTML = 'Your own statement. Now change the number.'; return; }
      if (build === 'bad') {
        page.classList.add('leak');
        page.innerHTML = `<b>Statement of ${NM[id]}</b><br>Balance ₹ ${(id * 37 % 90000 + 1000).toLocaleString('en-IN')} · account ${id}`;
        msg.innerHTML = '<b>🚨 Critical bug: broken access control.</b> Asha can read another customer\'s statement just by changing a number. The server only checked that someone was logged in, not whose account it was. This is number one on the OWASP Top 10.';
      } else {
        page.classList.add('deny');
        page.innerHTML = '<b>403 Forbidden</b> You can only view your own accounts.';
        msg.innerHTML = '<b>✅ Fixed.</b> The server checks that account ' + esc(id) + ' belongs to the logged in user before sending any data. Retest the same steps on every page that takes an id.';
      }
    };
    K.wireSeg(b, 'b', v => { build = v; go(); });
    b.addEventListener('click', e => {
      const t = e.target.closest('[data-t]'); if (t) { $('[data-id]', b).value = t.dataset.t; go(); return; }
      if (e.target.closest('[data-a="go"]')) go();
    });
    $('[data-id]', b).addEventListener('keydown', e => { if (e.key === 'Enter') go(); });
    go();
  };

  /* ----- making production data safe for testing ----- */
  W.mask = el => {
    const b = K.shell(el, 'Make real customer data safe to test with', 'Production data is copied for testing. Pick a technique and see what the testers would receive.');
    const R = [['Priya Sharma', '98450 12345', 'priya.s@mail.example', '5021'], ['Arjun Rao', '99001 67890', 'arjun.r@mail.example', '7734'], ['Lena Fischer', '91234 55555', 'lena.f@mail.example', '0918']];
    const T = {
      raw: ['Raw copy', R, '🚫 Not allowed. Real names, phones and emails reach every tester and test server. This breaks privacy laws such as GDPR in Europe and the DPDP Act in India.'],
      mask: ['Masking', R.map(r => [r[0][0] + '**** ' + r[0].split(' ')[1][0] + '****', 'XXXXX X' + r[1].slice(-4), r[2][0] + '*****@mail.example', '****']), 'Safe, but the data no longer looks real, and some checks (such as name search) become harder.'],
      sub: ['Substitution', [['Kavya Nair', '90000 11111', 'kavya.n@test.example', '1111'], ['Rohan Das', '90000 22222', 'rohan.d@test.example', '2222'], ['Mia Weber', '90000 33333', 'mia.w@test.example', '3333']], 'Values are replaced with realistic fakes of the same format. The app behaves normally and nobody is exposed.'],
      shuf: ['Shuffling', R.map((r, i) => [R[(i + 1) % 3][0], R[(i + 2) % 3][1], R[i][2], R[(i + 1) % 3][3]]), 'Columns are mixed between rows. It looks real, but small tables can still be pieced back together, so it is weaker.'],
      syn: ['Synthetic data', [['Test User 001', '90000 00001', 'user001@test.example', '0001'], ['Test User 002', '90000 00002', 'user002@test.example', '0002'], ['Edge Case Ünïcødé', '90000 00003', 'o\'brien+tag@test.example', '0003']], 'Generated from scratch, with no link to a real person. It can include edge cases that real data never had, like accents and apostrophes.']
    };
    b.innerHTML = `<div class="vz-row">${K.seg('t', Object.entries(T).map(([k, v]) => [k, v[0]]), 'raw')}</div><div class="m2-mk"></div><div class="vz-msg" aria-live="polite"></div>`;
    const draw = k => {
      const [, rows, why] = T[k];
      $('.m2-mk', b).innerHTML = `<div class="tw"><table class="jt"><tr><th>Name</th><th>Phone</th><th>Email</th><th>Card ends</th></tr>${rows.map(r => `<tr class="${k === 'raw' ? 'm2-hot' : ''}">${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table></div>`;
      $('.vz-msg', b).innerHTML = why;
    };
    K.wireSeg(b, 't', draw);
    draw('raw');
  };
})();
