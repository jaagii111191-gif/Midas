// unegui.mn машины үнэлгээний загварыг шинэчлэх скрипт (v4).
// Хэрэглэх: Chrome-оор https://www.unegui.mn нээгээд DevTools Console (F12) дээр
// энэ файлыг бүтнээр нь хуулж буулгана. 6–10 минутын дараа console дээр
// шинэ коэффициент, нарийвчлал, зарын шалгалтын JSON хэвлэгдэнэ.
// Түүнийг model_YYYY-MM-DD_v4.json болгон хадгалж, unelgee.html доторх C, RQ, YC-г солино.
// Татсан зарууд unegui.mn-ийн IndexedDB ("carval" → "D") дотор хадгалагдана.
// Дахин татахгүйгээр зөвхөн загвар сургах бол REUSE = true болго.

const NOW = 2026;      // ← жил солигдоход шинэчил
const REUSE = false;
const FRESH_ONLY = true;   // true: зөвхөн NOW онд орж ирсэн, "Дугаар аваагүй" зар (тооцоолуурын v5 хүрээ)

(async () => {
  const idb = {
    open: () => new Promise((res, rej) => { const r = indexedDB.open('carval', 1); r.onupgradeneeded = () => r.result.createObjectStore('kv'); r.onsuccess = () => res(r.result); r.onerror = rej; }),
    set: async (k, v) => { const db = await idb.open(); return new Promise((res, rej) => { const t = db.transaction('kv', 'readwrite'); t.objectStore('kv').put(v, k); t.oncomplete = res; t.onerror = rej; }); },
    get: async k => { const db = await idb.open(); return new Promise((res, rej) => { const r = db.transaction('kv').objectStore('kv').get(k); r.onsuccess = () => res(r.result); r.onerror = rej; }); }
  };

  // ---------- 1. Татах ----------
  const detail = async (u) => {
    const h = await fetch(u).then(r => r.text());
    const d = new DOMParser().parseFromString(h, 'text/html');
    const title = d.title;
    const pm = title.match(/([\d.,]+)\s*сая ₮/);
    d.querySelectorAll('script,style').forEach(e => e.remove());
    const t = d.body.textContent.replace(/\s+/g, ' ');
    const g = k => { const m = t.match(new RegExp(k + ':\\s*(.*?)(?=[А-ЯӨҮA-Z][а-яөүa-z ]{2,25}:|Тайлбар)')); return m ? m[1].trim() : null; };
    const i = t.indexOf('Тайлбар');
    return { u, title: title.split(' №')[0], price: pm ? parseFloat(pm[1].replace(',', '.')) : null,
      cc: g('Мотор багтаамж'), color: g('Өнгө'), made: g('Үйлдвэрлэсэн он'), imp: g('Орж ирсэн он'),
      km: g('Явсан'), cond: g('Нөхцөл'), drive: g('Хөтлөгч'), fuel: g('Хөдөлгүүр'), lease: g('Лизинг'),
      wheel: g('Хүрд'), inner: g('Дотор өнгө'), trans: g('Хурдны хайрцаг'), type: g('Төрөл'), doors: g('Хаалга'),
      desc: i >= 0 ? t.slice(i + 7, i + 3000) : '' };
  };
  const links = async (path, pat) => {
    const all = new Set();
    for (let p = 1; p <= 20; p++) {
      const h = await fetch(path + '?page=' + p).then(r => r.text());
      const before = all.size;
      (h.match(/\/adv\/\d+_[^"'\s\\]*/g) || []).filter(x => pat.test(x)).forEach(x => all.add(x));
      if (all.size === before) break;
    }
    return [...all];
  };
  let D = REUSE ? (await idb.get('D')) || [] : [];
  if (!REUSE) {
    const B = '/avto-mashin/-avtomashin-zarna/toyota/';
    const S = [['prius-40', /toyota-prius-40-/], ['prius-41', /toyota-prius-41-/], ['50', /toyota-prius-50-/],
               ['prius-51', /toyota-prius-51-/], ['camry', /toyota-camry-/], ['harrier', /toyota-harrier-/]];
    for (const [s, pat] of S) {
      const ls = await links(B + s + '/', pat);
      console.log(s, ls.length, 'зар');
      for (let i = 0; i < ls.length; i += 6) {
        const r = await Promise.all(ls.slice(i, i + 6).map(u => detail(u).catch(() => null)));
        r.forEach(x => x && D.push({ ...x, slug: s }));
      }
    }
    await idb.set('D', D); await idb.set('D_date', new Date().toISOString());
  }

  // ---------- 2. Шинж гаргах ----------
  const FAM = { 'prius-40': 'alpha', 'prius-41': 'alpha', '50': 'p50', 'prius-51': 'p50', camry: 'camry', harrier: 'harrier' };
  const L = '(?<![A-Za-z0-9.])', R = '(?![A-Za-z0-9])', ctx = '[\\s\\-_]*(загвар|zagvar|grade|грейд|grede|тохиргоо|комплект|zereg|зэрэг)';
  // Дарааллаар нь шалгана: эхэнд нь илүү тодорхой нэр.
  const GRADES = {
    alpha: [['gs', /g['’]?s(?![a-z])|ж[иэ]\s?эс\b/i], ['gtour', /\bg[\s\-_]*(touring|туринг|tour)/i], ['stour', /\bs[\s\-_]*(touring|туринг|tour)/i],
      ['tune', /tune\s*b|тюн/i], ['lsel', /\bl[\s\-]*(selection|селекшн|select)|s\s*l\s*sel/i],
      ['g', new RegExp('(бүтэн|buten|full)\\s*g' + R + '|' + L + 'G' + ctx + '|' + L + 'G' + R, 'i')],
      ['s', new RegExp(L + 'S' + ctx + '|' + L + 'S' + R + '(?![\\s\\-]*(series|safety|сер|ser\\b|l\\b))')],
      ['l', new RegExp('(?<!\\d\\s?)' + L + 'L' + ctx + '|(?<![\\d.]\\s?)' + L + 'L' + R + '(?![\\s\\-]*(package|пакет|сел|sel))')]],
    p50: [['apt', /a\s*premium\s*tour/i], ['aprem', /\ba\s*premium|а\s*премиум|premium/i], ['atour', /\ba[\s\-]*(touring|туринг)/i],
      ['stour', /\bs[\s\-]*(touring|туринг)/i], ['ssafe', /s\s*safety/i],
      ['a', new RegExp(L + 'A' + ctx + '|' + L + 'A' + R + '(?![\\s\\-]*(premium|touring))')],
      ['e', new RegExp(L + 'E' + ctx + '|' + L + 'E' + R)], ['s', new RegExp(L + 'S' + ctx + '|' + L + 'S' + R)]],
    camry: [['wsl', /ws\s*leather/i], ['ws', /\bws\b/i], ['gl', /g\s*(leather|лезер)|leather\s*package|арьсан\s*пакет/i],
      ['g', new RegExp('(бүтэн|buten|full)\\s*g' + R + '|' + L + 'G' + ctx + '|' + L + 'G' + R, 'i')], ['x', new RegExp(L + 'X' + ctx + '|' + L + 'X' + R)]],
    harrier: [['zl', /z\s*(leather|лезер)/i], ['z', new RegExp(L + 'Z' + ctx + '|' + L + 'Z' + R)], ['gl', /(?<![a-z])g\s*(leather|лезер)/i],
      ['pmetal', /progress\s*metal|metal\s*(and|&)\s*leather/i], ['progress', /progress|прогресс/i],
      ['padv', /premium\s*advanced|advanced\s*package|advanced|адванс/i], ['premium', /premium|премиум/i],
      ['elegance', /elegance|элеганс/i], ['grand', /grand|гранд/i], ['airs', /\bairs\b|эйрс/i], ['lpkg', /\bl[\s\-]*(package|пакет)/i],
      ['g', new RegExp(L + 'G' + ctx + '|' + L + 'G' + R)], ['s', new RegExp(L + 'S' + ctx + '|' + L + 'S' + R)]]
  };
  const BASEG = { alpha: 's', p50: 's', camry: 'g', harrier: 'premium' };   // комплектацын суурь
  const gradeOf = (fam, s) => { for (const [k, re] of GRADES[fam]) if (re.test(s)) return k; return ''; };

  const prep = a => {
    const fam = FAM[a.slug];
    let s = a.desc || '';
    const cut = s.lastIndexOf(String(a.price) + ' сая ₮'); if (cut >= 0) s = s.slice(0, cut);   // хуудсан дээрх үнийг тайлбараас салгах
    const fresh = /аваагүй|00 гүйлт/.test(a.cond || '');
    const ck = /аваагүй/.test(a.cond || '') ? 'fresh' : /00/.test(a.cond || '') ? 'z00' : /Дугаартай нь/.test(a.cond || '') ? 'withplate' : 'reg';
    const made = +a.made, imp = +a.imp;
    let km = parseInt((a.km || '').replace(/\D/g, '')) || null, kmFixed = false;
    if (km !== null && km < 1000) { km *= 1000; kmFixed = true; }   // "198 км" = 198,000 км
    const sc = (() => { const m = s.match(/(\d(?:[.,]5)?)\s*(?:оноо|үнэлгээ|grade|балл|unelgee|onoo|одтой)|(?:оноо|үнэлгээ|балл|аукцион|auction|unelgee|onoo)[^\d]{0,12}(\d(?:[.,]5)?)/i); if (!m) return null; const v = parseFloat((m[1] || m[2]).replace(',', '.')); return v >= 3 && v <= 5 ? v : null; })();
    return { u: a.u, slug: a.slug, fam, price: a.price, made, imp, km, kmFixed, fresh, color: a.color, cc: a.cc,
      impBad: imp && imp < made,
      ymn: fresh ? 0 : Math.max(0, NOW - Math.max(imp || made, made)),
      is40: a.slug === 'prius-40', is51: a.slug === 'prius-51', gas: a.fuel === 'Бензин',
      awd: /Бүх дугуй/.test(a.drive || '') || /e-?four|4wd|4x4/i.test(s),
      cc35: /^3\.[3-5]/.test(a.cc || ''), cc20: /^2\.0/.test(a.cc || ''),
      ub: !fresh && /\d{4}\s*У[А-ЯӨҮ]{2}|УБ[\s-]*(дугаар|сери|-ын)|Улаанбаатар[а-я]*\s*дугаар|ub\s*dugaar/i.test(s),
      roof: /люк|sunroof|moon ?roof|luk\b|шил дээвэр|skylight|панорам[а-я]*\s*(дээвэр|люк)/i.test(s), jbl: /jbl/i.test(s),
      cam360: /360|олон талын камер|panoramic view|бүх талын камер/i.test(s), hud: /\bhud\b|head.?up|шилэн дээр|шилэнд тусгах/i.test(s),
      leather: /(арьс|савхи)[а-яөү]*\s*(суудал|салон)|leather\s*seat|arisan suudal|кожан/i.test(s),
      radar: /радар|radar|машин дагагч|adaptive|safety\s*sense|tss|pre.?crash/i.test(s),
      winter: /winter|өвлийн\s*(загвар|пакет)|өвлын\s*загвар/i.test(s), led: /\bled\b|лед/i.test(s),
      modellista: /modellista|моделлиста|gr\s*sport|tom'?s|bodykit|обвес/i.test(s),
      battery: /(батер[еэ]й|battery|baterei)[^.]{0,25}(шин|солисон|soliso|new|сольсон)|(шин[эийн]+|солисон|new)\s*(батер[еэ]й|battery)/i.test(s),
      dealer: /showroom|шоурум|motors\b|моторс|авто\s*салон|autosalon|car\s*(market|trade)|захиалгаар|захиалга\s*авна|victory|салбар|худалдааны\s*төв/i.test(s),
      urgent: /яаралтай|yaraltai|яарч|хямдхан|hymd|хямд\s*зарна/i.test(s),
      nego: /үнэ\s*(тохирно|ярина|хэлэлцэнэ|бага\s*зэрэг)|une\s*tohir/i.test(s), swap: /солино|soli?n[oa]|сольж/i.test(s),
      lease: a.lease || '', ck, wheel: a.wheel || '', inner: a.inner || '',
      colg: (c => /Сувдан/.test(c) ? 'pearl' : c === 'Цагаан' ? 'white' : c === 'Хар' ? 'black' : /саарал/i.test(c) ? 'gray' : c === 'Улаан' ? 'red' : /Хөх|Цэнхэр/i.test(c) ? 'blue' : /Хүрэн|Бор|Боронзон/.test(c) ? 'brown' : 'other')(a.color || ''),
      score: sc, grade: gradeOf(fam, s) };
  };

  // ---------- 3. Загвар ----------
  const FAMS = ['alpha', 'p50', 'camry', 'harrier'];
  const buildCols = rows => {
    const cols = [], add = (k, pen, v) => cols.push({ k, pen, v });
    FAMS.forEach(f => {
      add('int_' + f, 0, r => r.fam === f ? 1 : 0);
      add('yr_' + f, 0, r => r.fam === f ? r.made - 2015 : 0);
      add('km_' + f, .5, r => r.fam === f ? Math.log(Math.min(Math.max(r.km || 150000, 10000), 400000) / 150000) : 0);
      [...new Set(rows.filter(r => r.fam === f).map(r => r.made))].sort().forEach(y => add('y_' + f + '_' + y, 3, r => r.fam === f && r.made === y ? 1 : 0));
      GRADES[f].map(g => g[0]).concat(['']).filter(g => g !== BASEG[f]).forEach(g => add('g_' + f + '_' + (g || 'unk'), .3, r => r.fam === f && r.grade === g ? 1 : 0));
      add('lhd_' + f, .5, r => r.fam === f && r.wheel === 'Зөв' ? 1 : 0);
      add('ymnf_' + f, 2, r => r.fam === f && !r.fresh ? Math.min(r.ymn, 8) : 0);
    });
    add('gas_camry', 1, r => r.fam === 'camry' && r.gas ? 1 : 0);
    add('gas_harrier', 1, r => r.fam === 'harrier' && r.gas ? 1 : 0);
    add('cc35_harrier', 1, r => r.fam === 'harrier' && r.cc35 ? 1 : 0);
    add('cc20_harrier', 1, r => r.fam === 'harrier' && r.cc20 ? 1 : 0);
    ['ub', 'roof', 'jbl', 'cam360', 'hud', 'leather', 'radar', 'is40', 'is51', 'awd',
     'winter', 'led', 'modellista', 'battery', 'dealer', 'urgent', 'nego', 'swap'].forEach(b => add(b, 1, r => r[b] ? 1 : 0));
    ['pearl', 'white', 'black', 'gray', 'red', 'blue', 'brown'].forEach(c => add('c_' + c, .3, r => r.colg === c ? 1 : 0));
    ['ББСБ лизингтэй', 'Банкны лизингтэй', 'Хувь лизингтэй'].forEach(v => add('lease=' + v, .5, r => r.lease === v ? 1 : 0));
    ['withplate', 'z00'].forEach(v => add('cond=' + v, .5, r => r.ck === v ? 1 : 0));
    ['Саарал', 'Бусад', 'Шаргал', 'Цагаан шар', 'Бор'].forEach(v => add('inner=' + v, .5, r => r.inner === v ? 1 : 0));
    add('hasScore', 1, r => r.score ? 1 : 0); add('score', 1, r => r.score ? r.score - 4 : 0);
    [[1, 1], [2, 2], [3, 3], [4, 5], [6, 99]].forEach(([a, b]) => add('ymn_' + a, 1, r => !r.fresh && r.ymn >= a && r.ymn <= b ? 1 : 0));
    add('plated0', 1, r => !r.fresh && r.ymn === 0 ? 1 : 0);
    add('cc24_camry', 1, r => r.fam === 'camry' && /^2\.4/.test(r.cc || '') ? 1 : 0);
    add('kmpy', 1, r => { const age = Math.max(1, NOW - r.made); return r.km ? Math.min(r.km / age / 20000, 3) - 1 : 0; });
    add('lowkm', 1, r => r.km && r.km < 5000 ? 1 : 0);
    return cols;
  };
  const solve = (A, b) => { const n = b.length; for (let i = 0; i < n; i++) { let p = i; for (let j = i + 1; j < n; j++) if (Math.abs(A[j][i]) > Math.abs(A[p][i])) p = j; [A[i], A[p]] = [A[p], A[i]]; [b[i], b[p]] = [b[p], b[i]]; const d = A[i][i] || 1e-9; for (let j = i + 1; j < n; j++) { const f = A[j][i] / d; if (!f) continue; for (let k = i; k < n; k++) A[j][k] -= f * A[i][k]; b[j] -= f * b[i]; } } const x = Array(n).fill(0); for (let i = n - 1; i >= 0; i--) { let s = b[i]; for (let k = i + 1; k < n; k++) s -= A[i][k] * x[k]; x[i] = s / (A[i][i] || 1e-9); } return x; };
  const fit = (rows, cols, lam = 1) => { const p = cols.length, A = Array.from({ length: p }, () => Array(p).fill(0)), b = Array(p).fill(0); for (const r of rows) { const x = cols.map(c => c.v(r)), y = Math.log(r.price), nz = []; x.forEach((v, i) => { if (v) nz.push(i); }); for (const i of nz) { b[i] += x[i] * y; for (const j of nz) A[i][j] += x[i] * x[j]; } } cols.forEach((c, i) => A[i][i] += lam * c.pen + 1e-6); return solve(A, b); };
  const pred = (r, cols, beta) => cols.reduce((s, c, i) => s + c.v(r) * beta[i], 0);
  const med = v => { v = [...v].sort((a, b) => a - b); return v[Math.floor(v.length / 2)]; };
  const q = (v, f) => { v = [...v].sort((a, b) => a - b); return v[Math.floor(f * (v.length - 1))]; };

  const seen = new Set();
  const ALL = D.filter(a => a && a.price && !seen.has(a.u) && seen.add(a.u)).map(prep).filter(r => r.made >= 2003 && r.made <= NOW && r.price >= 4 && r.price <= 250)
    .filter(r => !FRESH_ONLY || (r.ck === 'fresh' && r.imp === NOW));
  const dk = new Set();
  const rows = ALL.filter(r => { const k = [r.fam, r.made, r.imp, r.km, r.color, r.fresh].join('|'); if (dk.has(k)) return false; dk.add(k); return true; })
    .filter(r => !(r.km > 450000) && !r.impBad);
  let cols = buildCols(rows), beta = fit(rows, cols);
  const res0 = rows.map(r => Math.log(r.price) - pred(r, cols, beta));
  const sd = Math.sqrt(res0.reduce((a, b) => a + b * b, 0) / res0.length);
  const clean = rows.filter((r, i) => Math.abs(res0[i]) < 3 * sd);

  // 5-fold шалгалт
  cols = buildCols(clean);
  const idx = clean.map((r, i) => i).sort((a, b) => ((a * 2654435761) % 997) - ((b * 2654435761) % 997));
  const errs = [];
  for (let k = 0; k < 5; k++) {
    const te = new Set(idx.filter((x, j) => j % 5 === k));
    const bb = fit(clean.filter((r, i) => !te.has(i)), cols);
    clean.forEach((r, i) => { if (te.has(i)) errs.push(Math.abs(Math.exp(pred(r, cols, bb)) / r.price - 1)); });
  }
  beta = fit(clean, cols);
  const res = clean.map(r => Math.log(r.price) - pred(r, cols, beta));
  const coef = Object.fromEntries(cols.map((c, i) => [c.k, +beta[i].toFixed(4)]));
  const yc = {}; clean.forEach(r => { yc[r.fam] = yc[r.fam] || {}; yc[r.fam][r.made] = (yc[r.fam][r.made] || 0) + 1; });

  // ---------- 4. Зарын шалгалт ----------
  const aud = ALL.filter(r => !(r.km > 450000) && !r.impBad).map(r => ({ u: r.u, price: r.price, pred: +Math.exp(pred(r, cols, beta)).toFixed(1) }))
    .map(a => ({ ...a, ratio: a.price / a.pred }));
  const cnt = f => aud.filter(f).length;
  const sorted = [...aud].sort((a, b) => a.ratio - b.ratio);

  console.log(JSON.stringify({
    scraped: new Date().toISOString().slice(0, 10), n: clean.length,
    cv: { mape: +med(errs).toFixed(4), within10: +(errs.filter(e => e < .1).length / errs.length).toFixed(3) },
    RQ: { p10: +q(res, .1).toFixed(3), p25: +q(res, .25).toFixed(3), p75: +q(res, .75).toFixed(3), p90: +q(res, .9).toFixed(3) },
    year_counts: yc,
    audit: { under20: cnt(a => a.ratio < .8), fair10: cnt(a => a.ratio >= .9 && a.ratio <= 1.1), over25: cnt(a => a.ratio > 1.25),
      km_in_thousands: ALL.filter(r => r.kmFixed).length, cheapest: sorted.slice(0, 12), priciest: sorted.slice(-12).reverse() },
    coef }));
})();
