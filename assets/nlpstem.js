/* ===== Stemmers for the NLP animations, ported line by line from NLTK 3.10 so the page gives the same stems as the
   lecture notebook: PorterStemmer() in its default NLTK_EXTENSIONS mode, and SnowballStemmer("english").
   porter(word, trace) returns the stem. When trace is an array, each step pushes [step name, word after the step]. ===== */
const NLSTEM = (() => {
  const V = new Set(['a', 'e', 'i', 'o', 'u']);
  const isCons = (w, i) => {
    if (V.has(w[i])) return false;
    if (w[i] === 'y') {
      let neg = false;
      while (i > 0 && w[i] === 'y') { neg = !neg; i--; }
      return (!V.has(w[i])) !== neg;
    }
    return true;
  };
  const flags = w => { const f = []; for (let i = 0; i < w.length; i++) { const ch = w[i]; f.push(V.has(ch) ? false : ch === 'y' ? (i === 0 ? true : !f[i - 1]) : true); } return f; };
  const measure = s => { const q = flags(s).map(c => c ? 'c' : 'v').join(''); return (q.match(/vc/g) || []).length; };
  const pos = s => measure(s) > 0;
  const hasV = s => !flags(s).every(Boolean);
  const dbl = w => w.length >= 2 && w[w.length - 1] === w[w.length - 2] && isCons(w, w.length - 1);
  const cvc = w => (w.length >= 3 && isCons(w, w.length - 3) && !isCons(w, w.length - 2) && isCons(w, w.length - 1) && !'wxy'.includes(w[w.length - 1])) ||
    (w.length === 2 && !isCons(w, 0) && isCons(w, 1));
  const cut = (w, suf) => suf ? w.slice(0, -suf.length) : w;
  function rules(w, list) {
    for (const [suf, rep, cond] of list) {
      if (suf === '*d' && dbl(w)) { const st = w.slice(0, -2); return !cond || cond(st) ? st + rep : w; }
      if (suf !== '*d' && w.endsWith(suf)) { const st = cut(w, suf); return !cond || cond(st) ? st + rep : w; }
    }
    return w;
  }
  const POOL = { sky: 'sky', skies: 'sky', dying: 'die', lying: 'lie', tying: 'tie', news: 'news', innings: 'inning', inning: 'inning', outings: 'outing', outing: 'outing', cannings: 'canning', canning: 'canning', howe: 'howe', proceed: 'proceed', exceed: 'exceed', succeed: 'succeed' };
  function s1a(w) {
    if (w.endsWith('ies') && w.length === 4) return cut(w, 'ies') + 'ie';
    return rules(w, [['sses', 'ss'], ['ies', 'i'], ['ss', 'ss'], ['s', '']]);
  }
  function s1b(w) {
    if (w.endsWith('ied')) return w.length === 4 ? cut(w, 'ied') + 'ie' : cut(w, 'ied') + 'i';
    if (w.endsWith('eed')) { const st = cut(w, 'eed'); return measure(st) > 0 ? st + 'ee' : w; }
    let ok = false, mid = w;
    for (const suf of ['ed', 'ing']) if (w.endsWith(suf)) { mid = cut(w, suf); if (hasV(mid)) { ok = true; break; } }
    if (!ok) return w;
    return rules(mid, [['at', 'ate'], ['bl', 'ble'], ['iz', 'ize'], ['*d', mid[mid.length - 1], () => !'lsz'.includes(mid[mid.length - 1])], ['', 'e', st => measure(st) === 1 && cvc(st)]]);
  }
  const s1c = w => rules(w, [['y', 'i', st => st.length > 1 && isCons(st, st.length - 1)]]);
  function s2(w) {
    if (w.endsWith('alli') && pos(cut(w, 'alli'))) return s2(cut(w, 'alli') + 'al');
    const L = [['ational', 'ate'], ['tional', 'tion'], ['enci', 'ence'], ['anci', 'ance'], ['izer', 'ize'], ['bli', 'ble'], ['alli', 'al'], ['entli', 'ent'], ['eli', 'e'], ['ousli', 'ous'],
      ['ization', 'ize'], ['ation', 'ate'], ['ator', 'ate'], ['alism', 'al'], ['iveness', 'ive'], ['fulness', 'ful'], ['ousness', 'ous'], ['aliti', 'al'], ['iviti', 'ive'], ['biliti', 'ble'], ['fulli', 'ful']].map(r => [r[0], r[1], pos]);
    L.push(['logi', 'log', () => pos(w.slice(0, -3))]);
    return rules(w, L);
  }
  const s3 = w => rules(w, [['icate', 'ic'], ['ative', ''], ['alize', 'al'], ['iciti', 'ic'], ['ical', 'ic'], ['ful', ''], ['ness', '']].map(r => [r[0], r[1], pos]));
  function s4(w) {
    const g = st => measure(st) > 1;
    return rules(w, [['al', '', g], ['ance', '', g], ['ence', '', g], ['er', '', g], ['ic', '', g], ['able', '', g], ['ible', '', g], ['ant', '', g], ['ement', '', g], ['ment', '', g], ['ent', '', g],
      ['ion', '', st => measure(st) > 1 && 'st'.includes(st[st.length - 1] || '#')], ['ou', '', g], ['ism', '', g], ['ate', '', g], ['iti', '', g], ['ous', '', g], ['ive', '', g], ['ize', '', g]]);
  }
  function s5a(w) {
    if (w.endsWith('e')) { const st = cut(w, 'e'); if (measure(st) > 1) return st; if (measure(st) === 1 && !cvc(st)) return st; }
    return w;
  }
  const s5b = w => rules(w, [['ll', 'l', () => measure(w.slice(0, -1)) > 1]]);
  function porter(word, trace) {
    let w = String(word).toLowerCase();
    const T = (n, x) => { if (trace) trace.push([n, x]); return x; };
    if (POOL[w] !== undefined) return T('irregular word list', POOL[w]);
    if (word.length <= 2) return T('too short to stem', w);
    w = T('Step 1a: plurals (sses, ies, s)', s1a(w));
    w = T('Step 1b: ed, ing, eed', s1b(w));
    w = T('Step 1c: y to i', s1c(w));
    w = T('Step 2: double suffixes (ational, izer, fulness)', s2(w));
    w = T('Step 3: ic, ful, ness, alize', s3(w));
    w = T('Step 4: al, ance, er, ment, ion (measure above 1)', s4(w));
    w = T('Step 5a: final e', s5a(w));
    w = T('Step 5b: ll to l', s5b(w));
    return w;
  }

  /* ---------- Snowball English (Porter2) ---------- */
  const SV = 'aeiouy';
  const isV = c => c !== undefined && SV.includes(c);
  const at = (w, k) => w[w.length - k];
  const sufRep = (w, s, r) => w.slice(0, w.length - s.length) + r;
  const SPECIAL = { skis: 'ski', skies: 'sky', dying: 'die', lying: 'lie', tying: 'tie', idly: 'idl', gently: 'gentl', ugly: 'ugli', early: 'earli', only: 'onli', singly: 'singl', sky: 'sky', news: 'news', howe: 'howe', atlas: 'atlas', cosmos: 'cosmos', bias: 'bias', andes: 'andes',
    inning: 'inning', innings: 'inning', outing: 'outing', outings: 'outing', canning: 'canning', cannings: 'canning', herring: 'herring', herrings: 'herring', earring: 'earring', earrings: 'earring',
    proceed: 'proceed', proceeds: 'proceed', proceeded: 'proceed', proceeding: 'proceed', exceed: 'exceed', exceeds: 'exceed', exceeded: 'exceed', exceeding: 'exceed', succeed: 'succeed', succeeds: 'succeed', succeeded: 'succeed', succeeding: 'succeed' };
  function r1r2(w) {
    let r1 = '', r2 = '';
    for (let i = 1; i < w.length; i++) if (!isV(w[i]) && isV(w[i - 1])) { r1 = w.slice(i + 1); break; }
    for (let i = 1; i < r1.length; i++) if (!isV(r1[i]) && isV(r1[i - 1])) { r2 = r1.slice(i + 1); break; }
    return [r1, r2];
  }
  const S2 = ['ization', 'ational', 'fulness', 'ousness', 'iveness', 'tional', 'biliti', 'lessli', 'entli', 'ation', 'alism', 'aliti', 'ousli', 'iviti', 'fulli', 'enci', 'anci', 'abli', 'izer', 'ator', 'alli', 'bli', 'ogi', 'li'];
  const S3 = ['ational', 'tional', 'alize', 'icate', 'iciti', 'ative', 'ical', 'ness', 'ful'];
  const S4 = ['ement', 'ance', 'ence', 'able', 'ible', 'ment', 'ant', 'ent', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize', 'ion', 'al', 'er', 'ic'];
  const DBL = ['bb', 'dd', 'ff', 'gg', 'mm', 'nn', 'pp', 'rr', 'tt'];
  function snowball(word) {
    let w = String(word).toLowerCase();
    if (w.length <= 2) return w;
    if (SPECIAL[w] !== undefined) return SPECIAL[w];
    w = w.replace(/[’‘‛]/g, "'");
    if (w.startsWith("'")) w = w.slice(1);
    if (w.startsWith('y')) w = 'Y' + w.slice(1);
    const ch = w.split('');
    for (let i = 1; i < ch.length; i++) if (SV.includes(ch[i - 1]) && ch[i] === 'y') ch[i] = 'Y';
    w = ch.join('');
    let r1 = '', r2 = '';
    if (/^(gener|commun|arsen)/.test(w)) {
      r1 = /^(gener|arsen)/.test(w) ? w.slice(5) : w.slice(6);
      for (let i = 1; i < r1.length; i++) if (!isV(r1[i]) && isV(r1[i - 1])) { r2 = r1.slice(i + 1); break; }
    } else [r1, r2] = r1r2(w);
    const chop = n => { w = w.slice(0, -n); r1 = r1.slice(0, -n); r2 = r2.slice(0, -n); };
    const repl = (s, r, r2else = '') => { w = sufRep(w, s, r); r1 = r1.length >= s.length ? sufRep(r1, s, r) : ''; r2 = r2.length >= s.length ? sufRep(r2, s, r) : r2else; };
    for (const s of ["'s'", "'s", "'"]) if (w.endsWith(s)) { chop(s.length); break; }
    for (const s of ['sses', 'ied', 'ies', 'us', 'ss', 's']) if (w.endsWith(s)) {
      if (s === 'sses') chop(2);
      else if (s === 'ied' || s === 'ies') { if (w.slice(0, -s.length).length > 1) chop(2); else chop(1); }
      else if (s === 's') { if ([...w.slice(0, -2)].some(isV)) chop(1); }
      break;
    }
    for (const s of ['eedly', 'ingly', 'edly', 'eed', 'ing', 'ed']) if (w.endsWith(s)) {
      if (s === 'eed' || s === 'eedly') { if (r1.endsWith(s)) repl(s, 'ee'); }
      else if ([...w.slice(0, -s.length)].some(isV)) {
        chop(s.length);
        if (/(at|bl|iz)$/.test(w)) { w += 'e'; r1 += 'e'; if (w.length > 5 || r1.length >= 3) r2 += 'e'; }
        else if (DBL.some(d => w.endsWith(d))) chop(1);
        else if ((r1 === '' && w.length >= 3 && !isV(at(w, 1)) && !'wxY'.includes(at(w, 1)) && isV(at(w, 2)) && !isV(at(w, 3))) ||
          (r1 === '' && w.length === 2 && isV(w[0]) && !isV(w[1]))) { w += 'e'; if (r1.length) r1 += 'e'; if (r2.length) r2 += 'e'; }
      }
      break;
    }
    if (w.length > 2 && 'yY'.includes(at(w, 1)) && !isV(at(w, 2))) {
      w = w.slice(0, -1) + 'i'; r1 = r1.length >= 1 ? r1.slice(0, -1) + 'i' : ''; r2 = r2.length >= 1 ? r2.slice(0, -1) + 'i' : '';
    }
    for (const s of S2) if (w.endsWith(s)) {
      if (r1.endsWith(s)) {
        if (s === 'tional' || s === 'entli' || s === 'fulli' || s === 'lessli') chop(2);
        else if (s === 'enci' || s === 'anci' || s === 'abli') { w = w.slice(0, -1) + 'e'; r1 = r1.length >= 1 ? r1.slice(0, -1) + 'e' : ''; r2 = r2.length >= 1 ? r2.slice(0, -1) + 'e' : ''; }
        else if (s === 'izer' || s === 'ization') repl(s, 'ize');
        else if (s === 'ational' || s === 'ation' || s === 'ator') repl(s, 'ate', 'e');
        else if (s === 'alism' || s === 'aliti' || s === 'alli') repl(s, 'al');
        else if (s === 'fulness') chop(4);
        else if (s === 'ousli' || s === 'ousness') repl(s, 'ous');
        else if (s === 'iveness' || s === 'iviti') repl(s, 'ive', 'e');
        else if (s === 'biliti' || s === 'bli') repl(s, 'ble');
        else if (s === 'ogi' && at(w, 4) === 'l') chop(1);
        else if (s === 'li' && at(w, 3) !== undefined && 'cdeghkmnrt'.includes(at(w, 3))) chop(2);
      }
      break;
    }
    for (const s of S3) if (w.endsWith(s)) {
      if (r1.endsWith(s)) {
        if (s === 'tional') chop(2);
        else if (s === 'ational') repl(s, 'ate');
        else if (s === 'alize') chop(3);
        else if (s === 'icate' || s === 'iciti' || s === 'ical') repl(s, 'ic');
        else if (s === 'ful' || s === 'ness') chop(s.length);
        else if (s === 'ative' && r2.endsWith(s)) chop(5);
      }
      break;
    }
    for (const s of S4) if (w.endsWith(s)) {
      if (r2.endsWith(s)) {
        if (s === 'ion') { if (at(w, 4) !== undefined && 'st'.includes(at(w, 4))) chop(3); }
        else chop(s.length);
      }
      break;
    }
    if (r2.endsWith('l') && at(w, 2) === 'l') w = w.slice(0, -1);
    else if (r2.endsWith('e')) w = w.slice(0, -1);
    else if (r1.endsWith('e')) {
      if (w.length >= 4 && (isV(at(w, 2)) || 'wxY'.includes(at(w, 2)) || !isV(at(w, 3)) || isV(at(w, 4)))) w = w.slice(0, -1);
    }
    return w.replace(/Y/g, 'y');
  }
  return { porter, snowball, measure };
})();
if (typeof module !== 'undefined') module.exports = NLSTEM;
