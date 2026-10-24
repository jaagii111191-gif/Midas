// unegui.mn-ээс Toyota-гийн зарыг дахин татаж, нэг JSON файл болгон татах скрипт (2026-10-24-өөс).
// Desktop апп шаардлагагүй: зөвхөн Chrome хэрэгтэй.
// Хэрэглэх:
//   1. Chrome-оор https://www.unegui.mn нээнэ (Cloudflare шалгалтыг давсан байх ёстой).
//   2. F12 → Console. Хэрэв "allow pasting" гэж асуувал түүнийг бичээд Enter дарна.
//   3. Энэ файлыг бүтнээр нь хуулж буулгаад Enter. 8–15 минут болно, console дээр явц хэвлэгдэнэ.
//   4. Дуусахад "unegui_toyota_<огноо>.json" Downloads хавтсанд бууна. Түүнийг Claude-д явуулна.
// Загварыг (v9 г.м.) энэ файлаас Python скриптүүдээр (tools/) сургана.
// Дэлгэрэнгүй хуудсыг <dt>/<dd> бүтцээр уншина. Олдохгүй бол хуучин текст уншигч руу шилжинэ.

const NOW = 2026;      // ← жил солигдоход шинэчил

(async () => {
  const KEYS = ['Мотор багтаамж', 'Хурдны хайрцаг', 'Хүрд', 'Төрөл', 'Өнгө', 'Үйлдвэрлэсэн он', 'Орж ирсэн он',
    'Хөдөлгүүр', 'Дотор өнгө', 'Лизинг', 'Хөтлөгч', 'Явсан', 'Нөхцөл', 'Хаалга'];
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const get = async u => { for (let t = 0; t < 3; t++) { const r = await fetch(u); if (r.ok) return r.text(); await sleep(1500 * (t + 1)); } throw new Error(u); };

  // ---------- 1. Татах ----------
  const detail = async (u) => {
    const h = await get(u);
    const d = new DOMParser().parseFromString(h, 'text/html');
    const title = d.title;
    const pm = title.match(/([\d.,]+)\s*сая ₮/);
    const at = {};
    d.querySelectorAll('dt').forEach(dt => { const dd = dt.nextElementSibling; const k = dt.textContent.replace(/[:\s]+$/, '').trim(); if (dd && dd.tagName === 'DD' && k) at[k] = dd.textContent.replace(/\s+/g, ' ').trim(); });
    d.querySelectorAll('script,style').forEach(e => e.remove());
    const t = d.body.textContent.replace(/\s+/g, ' ');
    if (!at['Үйлдвэрлэсэн он']) KEYS.forEach(k => {   // хуучин бүтэц
      const m = t.match(new RegExp(k + ':\\s*(.*?)(?=[А-ЯӨҮA-Z][а-яөүa-z ]{2,25}:|Тайлбар)')); if (m) at[k] = m[1].trim(); });
    const i = t.indexOf('Тайлбар');
    return { u, title: title.split(' №')[0], price: pm ? parseFloat(pm[1].replace(',', '.')) : null, at,
      desc: i >= 0 ? t.slice(i + 7, i + 3000) : '' };
  };
  const links = async (path, pat) => {
    const all = new Set();
    for (let p = 1; p <= 30; p++) {
      const h = await get(path + '?page=' + p);
      const before = all.size;
      (h.match(/\/adv\/\d+_[^"'\s\\]*/g) || []).filter(x => pat.test(x)).forEach(x => all.add(x.endsWith('/') ? x : x + '/'));
      if (all.size === before) break;
    }
    return [...all];
  };
  const B = '/avto-mashin/-avtomashin-zarna/toyota/';
  const S = [['prius-40', /toyota-prius-40-/], ['prius-41', /toyota-prius-41-/], ['50', /toyota-prius-50-/],
             ['prius-51', /toyota-prius-51-/], ['Prius55', /toyota-prius-55-/], ['camry', /toyota-camry-/], ['harrier', /toyota-harrier-/]];
  const D = [], seenU = new Set();
  for (const [s, pat] of S) {
    const ls = (await links(B + s + '/', pat)).filter(u => !seenU.has(u));
    ls.forEach(u => seenU.add(u));
    console.log(s, ls.length, 'зар');
    for (let i = 0; i < ls.length; i += 6) {
      const r = await Promise.all(ls.slice(i, i + 6).map(u => detail(u).catch(() => null)));
      r.forEach(x => x && D.push({ ...x, slug: s }));
      if (i % 60 === 0) console.log('  ', s, Math.min(i + 6, ls.length), '/', ls.length);
    }
  }
  const noAt = D.filter(a => !a.at['Үйлдвэрлэсэн он']).length;
  console.log('Нийт', D.length, 'зар. Талбар уншиж чадаагүй:', noAt);

  // ---------- 2. Шинж гаргах ----------
  const FAM = { 'prius-40': 'alpha', 'prius-41': 'alpha', '50': 'p50', 'prius-51': 'p50', Prius55: 'p50', camry: 'camry', harrier: 'harrier' };
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

  const flat = a => ({ ...a, cc: a.at['Мотор багтаамж'], color: a.at['Өнгө'], made: a.at['Үйлдвэрлэсэн он'], imp: a.at['Орж ирсэн он'],
    km: a.at['Явсан'], cond: a.at['Нөхцөл'], drive: a.at['Хөтлөгч'], fuel: a.at['Хөдөлгүүр'], lease: a.at['Лизинг'],
    wheel: a.at['Хүрд'], inner: a.at['Дотор өнгө'] });
  const prep = a0 => {
    const a = flat(a0), fam = FAM[a.slug];
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

  const P = [];
  for (const a of D) { if (!a.price) continue; try { P.push({ ...prep(a), is55: a.slug === 'Prius55' }); } catch (e) {} }
  const date = new Date().toISOString().slice(0, 10);
  const out = { exported: new Date().toISOString(), date, raw: D, prepped: P };
  const blob = new Blob([JSON.stringify(out)], { type: 'application/json' });
  const el = document.createElement('a');
  el.href = URL.createObjectURL(blob); el.download = 'unegui_toyota_' + date + '.json'; el.click();
  const fresh = P.filter(r => r.ck === 'fresh' && r.imp === NOW).length;
  console.log('Татлаа:', D.length, 'зар,', P.length, 'шинжтэй,', fresh, 'нь', NOW, 'онд орж ирсэн, дугаар аваагүй. Файл: unegui_toyota_' + date + '.json');
})();
