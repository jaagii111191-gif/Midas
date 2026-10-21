#!/usr/bin/env node
// Midas Motors poster CLI: turns 1000mashin.mn listings or a JSON file into 1080×1350 PNG posters.
// Run `npm run poster -- help` for usage.
const fs = require('fs');
const path = require('path');
const { root, DEFAULT_OUT, launchBrowser, newContext, renderEntries, readEntries } =
  require('../templates/midas-motors/render-posters.js');

const USAGE = `
Midas Motors постер гаргагч

  npm run poster -- url <1000mashin холбоос>            нэг машин, олон зурагтай постер (T7)
  npm run poster -- url <холбоос> --t1                   нэг машин, нэг зурагтай постер (T1)
  npm run poster -- lineup <холбоос> <холбоос> [...]     нэг постерт 2–6 машин (T8)
  npm run poster -- render <файл.json>                   JSON файлаас бүх постерыг гаргах
  npm run poster -- demo                                  гурван загварыг жишээ утгаар гаргах

Сонголтууд:
  --badge "ГААЛИАС ШУУД"     статусын шошгоны бичиг (анхдагч: ШИНЭ ИРСЭН)
  --badge-type customs       new · customs · lease · drop · out
  --labels "Ар тал,Салон"    жижиг зургуудын нэр, дарааллаар нь
  --title "Бэлэн 3 машин"    lineup постерын гарчиг
  --eyebrow "..."            lineup гарчгийн дээрх жижиг мөр
  --phone 9911-2233          утас (анхдагч: data/midas-config.json)
  --address "Хаяг: ..."      хаяг (анхдагч: data/midas-config.json)
  --out <хавтас>             гаралтын хавтас (анхдагч: reports/midas-posters)
  --scale 2                  2160×2700 хэмжээтэй, илүү тод гаргах

url/lineup команд үүсгэсэн өгөгдлөө data/generated/<id>.json-д хадгална.
Түүнийг засаад "render" командаар дахин гаргаж болно.
`;

function parseArgs(argv) {
  const flags = {}; const args = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--t1') flags.t1 = true;
    else if (a.startsWith('--')) flags[a.slice(2)] = argv[++i];
    else args.push(a);
  }
  return { cmd: args.shift(), args, flags };
}

function loadConfig() {
  const file = path.join(root, 'data', 'midas-config.json');
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch { return {}; }
}

// ---------- 1000mashin.mn listing → poster data ----------

const COLORS = { gold: 'Алтлаг', silver: 'Мөнгөлөг', black: 'Хар', white: 'Цагаан', pearl: 'Цагаан сувд', gray: 'Саарал',
  grey: 'Саарал', blue: 'Цэнхэр', red: 'Улаан', brown: 'Бор', beige: 'Шаргал', green: 'Ногоон', yellow: 'Шар', orange: 'Улбар шар' };

function decode(s) {
  return s.replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#039;/g, "'").replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\s+/g, ' ').trim();
}

// "PRIUS 51" → PRIUS / 51; Prius Alpha → PRIUS 40/41 from the frame code; Camry → 50/70 from the year.
function splitModel(mark, frame, yearMade) {
  const m = mark.toUpperCase().trim();
  if (/^PRIUS\s+(ALPHA|A|Α)$/.test(m)) {
    return { model: 'PRIUS', gen: /ZVW40/.test(frame) ? '40' : /ZVW41/.test(frame) ? '41' : 'α', trim: 'Prius α' };
  }
  if (/^CAMRY/.test(m)) {
    const y = Number(yearMade);
    return { model: 'CAMRY', gen: y >= 2018 ? '70' : y >= 2012 ? '50' : '', trim: /HYBRID/.test(m) ? 'Hybrid' : '' };
  }
  const parts = m.split(/\s+/);
  const last = parts[parts.length - 1];
  if (parts.length > 1 && /^\d+$/.test(last)) return { model: parts.slice(0, -1).join(' '), gen: last, trim: '' };
  return { model: m, gen: '', trim: '' };
}

function parseListing(html, url) {
  const specs = {};
  for (const m of html.matchAll(/spec__name">([^<]*)<\/div>\s*<div class="spec__value">([^<]*)<\/div>/g)) {
    specs[decode(m[1]).replace(/:$/, '')] = decode(m[2]);
  }
  const mark = specs['Марк'] || '';
  if (!mark) throw new Error('Зарын мэдээлэл олдсонгүй: ' + url);
  const photos = [];
  for (const m of html.matchAll(/\/uploads\/zar\/middle\/+(img-\d+-\d+\.(?:jpe?g|png|webp))/gi)) {
    const src = 'https://www.1000mashin.mn/uploads/zar/middle/' + m[1];
    if (!photos.includes(src)) photos.push(src);
  }
  const priceM = html.match(/product__price--current">([^<]*)</);
  const yearMade = (specs['Үйлдвэрлэсэн он'] || '').replace(/\D+$/, '');
  const { model, gen, trim } = splitModel(mark, specs['Арлын дугаар'] || '', yearMade);
  const cc = Number((specs['Мотор сс'] || '').replace(/[^\d]/g, ''));
  const hybrid = /HYBRID|PRIUS/i.test(mark) || /хайбрид|hybrid/i.test(specs['Шатахуун'] || '');
  const engine = cc ? (cc / 1000).toFixed(1) + (hybrid ? ' Hybrid' : '') : '';
  const drive = /мосттой/i.test(specs['Хөтлөгч'] || '') ? '4WD' : /мостгүй/i.test(specs['Хөтлөгч'] || '') ? '2WD' : '';
  const color = COLORS[(specs['Өнгө'] || '').toLowerCase()] || specs['Өнгө'] || '';
  const listingId = (url.match(/car-view\/(\d+)/) || [])[1] || String(Date.now());
  return {
    listingId, source: url, model, gen, trim, photos, color, engine, drive,
    year_made: yearMade, year_import: specs['Орж ирсэн'] || '',
    km: specs['Явсан км'] || '', joloo: specs['Жолоо'] || '', seats: specs['Суудал'] || '',
    price: priceM ? decode(priceM[1]).replace(/[^\d.]/g, '') : '',
    lease: html.includes('status-badge__text">Лизингтэй'),
  };
}

async function fetchListings(urls) {
  const browser = await launchBrowser();
  try {
    const page = await (await newContext(browser)).newPage();
    const out = [];
    for (const url of urls) {
      if (!/1000mashin\.mn\/car-view\/\d+/.test(url)) throw new Error('1000mashin.mn/car-view/... хэлбэрийн холбоос хэрэгтэй: ' + url);
      // The server HTML (not the script-modified page) lists every gallery photo. Flaky networks get a few spaced retries.
      let html = '';
      for (let attempt = 1; attempt <= 5 && !html.includes('spec__name'); attempt++) {
        try {
          const resp = await page.goto(url, { waitUntil: 'commit', timeout: 45000 });
          html = resp ? await resp.text() : '';
        } catch (e) {
          if (attempt === 5) throw e;
          await new Promise(r => setTimeout(r, 1500 * attempt));
        }
      }
      const car = parseListing(html, url);
      console.log(`• ${car.model} ${car.gen} · ${car.year_made}/${car.year_import} · ${car.km} · ${car.price} сая · ${car.photos.length} зураг`);
      out.push(car);
    }
    return out;
  } finally {
    await browser.close();
  }
}

function slug(car) { return [car.model, car.gen, car.listingId].filter(Boolean).join('-').toLowerCase().replace(/[^a-z0-9α-]+/g, '-'); }

function carEntry(car, flags, cfg) {
  const third = car.trim === 'Prius α' && car.seats ? ['Суудал', car.seats] : ['Хөтлөгч', car.drive || '—'];
  const labels = (flags.labels || '').split(',').map(s => s.trim()).filter(Boolean);
  const template = flags.t1 ? 't1' : 'multi';
  return {
    id: `${slug(car)}-${template}`,
    _source: car.source,
    template,
    photos: car.photos.map((src, i) => (i > 0 && labels[i - 1] ? { src, label: labels[i - 1] } : src)),
    model: car.model, gen: car.gen, trim: car.trim,
    year_made: car.year_made, year_import: car.year_import, color: car.color,
    specs: [['Явсан', car.km], ['Мотор', car.engine || '—'], third, ['Жолоо', car.joloo || '—']],
    price: car.price,
    badge: flags['badge-type'] || 'new',
    badge_text: flags.badge || 'ШИНЭ ИРСЭН',
    lease_title: car.lease ? 'ЛИЗИНГТЭЙ' : '',
    lease_sub: car.lease ? 'Банк, ББСБ-ын лизинг' : '',
    phone: flags.phone || cfg.phone || 'XXXX-XXXX',
    address: flags.address || cfg.address || 'Хаяг: {{ hayag }}',
  };
}

function lineupEntry(cars, flags, cfg) {
  return {
    id: 'lineup-' + cars.map(c => c.listingId).join('-'),
    template: 'lineup',
    badge: flags['badge-type'] || 'new',
    badge_text: flags.badge || '',
    eyebrow: flags.eyebrow || 'Энэ долоо хоногт ирсэн',
    title: flags.title || `Бэлэн ${cars.length} машин`,
    phone: flags.phone || cfg.phone || 'XXXX-XXXX',
    address: flags.address || cfg.address || 'Хаяг: {{ hayag }}',
    cars: cars.map(c => ({
      _source: c.source, photo: c.photos[0] || '', model: c.model, gen: c.gen,
      year_made: c.year_made, year_import: c.year_import, km: c.km, price: c.price,
      ...(c.lease ? { tag: 'lease', tag_text: 'ЛИЗИНГТЭЙ' } : {}),
    })),
  };
}

function saveGenerated(entries) {
  const dir = path.join(root, 'data', 'generated');
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, entries[0].id + '.json');
  fs.writeFileSync(file, JSON.stringify({ cars: entries }, null, 2) + '\n');
  console.log('  өгөгдөл: ' + path.relative(process.cwd(), file));
}

async function main() {
  const { cmd, args, flags } = parseArgs(process.argv.slice(2));
  const cfg = loadConfig();
  const opts = { out: flags.out ? path.resolve(flags.out) : DEFAULT_OUT, scale: Number(flags.scale) || 1 };

  if (cmd === 'url') {
    if (!args.length) throw new Error('Холбоос өгнө үү. Жишээ: npm run poster -- url https://www.1000mashin.mn/car-view/11918/x');
    const entries = (await fetchListings(args)).map(c => carEntry(c, flags, cfg));
    entries.forEach(e => saveGenerated([e]));
    return renderEntries(entries, opts);
  }
  if (cmd === 'lineup') {
    if (args.length < 2 || args.length > 6) throw new Error('lineup-д 2–6 холбоос хэрэгтэй.');
    const entry = lineupEntry(await fetchListings(args), flags, cfg);
    saveGenerated([entry]);
    return renderEntries([entry], opts);
  }
  if (cmd === 'render') {
    if (!args[0]) throw new Error('JSON файлын зам өгнө үү. Жишээ: npm run poster -- render data/midas-examples-1000mashin.json');
    return renderEntries(readEntries(args[0]), opts);
  }
  if (cmd === 'demo') {
    return renderEntries([
      { id: 'demo-t1', template: 't1' },
      { id: 'demo-multi', template: 'multi', model: 'PRIUS', gen: '51', trim: 'S', year_made: '2017', year_import: '2025', color: 'Мөнгөлөг',
        specs: [['Явсан', '98,000 км'], ['Мотор', '1.8 Hybrid'], ['Хөтлөгч', '2WD'], ['Жолоо', 'Буруу']], price: '38.5',
        badge: 'customs', badge_text: 'ГААЛИАС ШУУД', lease_title: 'ЛИЗИНГТЭЙ', lease_sub: 'Урьдчилгаа 30%-иас',
        phone: cfg.phone || 'XXXX-XXXX', address: cfg.address || 'Хаяг: {{ hayag }}', photos: ['', '', '', ''] },
      { id: 'demo-lineup', template: 'lineup', badge: 'new', badge_text: '10.06 – 10.12', eyebrow: 'Энэ долоо хоногт ирсэн', title: 'Бэлэн 3 машин',
        phone: cfg.phone || 'XXXX-XXXX', address: cfg.address || 'Бүгд лизингтэй',
        cars: [{ model: 'PRIUS', gen: '51', year_made: '2017', year_import: '2025', km: '98,000 км', price: '38.5', tag: 'lease', tag_text: 'ЛИЗИНГТЭЙ' },
               { model: 'PRIUS', gen: '41', year_made: '2016', year_import: '2025', km: '77,000 км', price: '36.0' },
               { model: 'CAMRY', gen: '50', year_made: '2015', year_import: '2025', km: '170,000 км', price: '40.0' }] },
    ], opts);
  }
  console.log(USAGE);
  if (cmd && cmd !== 'help') process.exitCode = 1;
}

main().catch(e => { console.error('✗ ' + (e && e.message ? e.message : e)); process.exit(1); });
