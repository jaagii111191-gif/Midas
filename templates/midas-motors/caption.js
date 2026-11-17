// Midas Motors Facebook-ийн зарын тайлбар (caption) үүсгэгч.
// Нэг файл хоёр газар ажиллана: вэб хуудас (caption.html) болон терминал (bin/midas-poster.js caption).
//   buildCaption(cars, opts) → { long, short }
//   fromPosterEntry(entry)   → { cars, opts }   постерын JSON (data/*.json)-ийн нэг мөрөөс
(function (root) {
  'use strict';

  // Загварын бэлэн утга. "why" нь зөвхөн баталгаатай мэдээлэл, бусад загварт хэрэглэгч өөрөө бичнэ.
  const PRESETS = {
    prius41: {
      name: 'Toyota Prius α (Prius 41)', label: 'PRIUS 41', frame: 'ZVW41', engine: '1.8 Hybrid', seats: '5',
      tags: ['Prius41', 'PriusAlpha', 'Приус41', 'Хайбрид'],
      whyTitle: 'Яагаад Prius α гэж?',
      why: [
        'Энгийн Prius-аас урт, өндөр их биетэй тул тээш болон хойд суудал нь илүү зайтай.',
        '1.8 хайбрид хөдөлгүүр: үйлдвэрийн үзүүлэлтээр 26.2 км/л (JC08).',
        'Хотын удаан хөдөлгөөнд цахилгаан мотор их ажилладаг тул түгжрэлд шатахуун хэмнэнэ.',
      ],
    },
    prius30: { name: 'Toyota Prius (Prius 30)', label: 'PRIUS 30', frame: 'ZVW30', engine: '1.8 Hybrid', seats: '5', tags: ['Prius30', 'Приус30', 'Хайбрид'] },
    prius51: { name: 'Toyota Prius (Prius 51)', label: 'PRIUS 51', frame: 'ZVW51', engine: '1.8 Hybrid', seats: '5', tags: ['Prius51', 'Приус51', 'Хайбрид'] },
    camry50: { name: 'Toyota Camry Hybrid (Camry 50)', label: 'CAMRY 50', frame: 'AVV50', engine: '2.5 Hybrid', seats: '5', tags: ['Camry50', 'Камри50', 'Хайбрид'] },
    camry70: { name: 'Toyota Camry Hybrid (Camry 70)', label: 'CAMRY 70', frame: 'AXVH70', engine: '2.5 Hybrid', seats: '5', tags: ['Camry70', 'Камри70', 'Хайбрид'] },
  };

  const PAYMENT = [
    'Урьдчилгаа 30% төлж захиалгаа баталгаажуулна.',
    'Үлдэгдэл төлбөрийг машин Монголд буусны дараа төлнө.',
  ];
  const LOAN = 'Банк бус санхүүгийн байгууллагын зээлд зуучилж өгнө.';

  const s = v => (v == null ? '' : String(v)).trim();

  // "22" → "22.0", "22.45" → "22.45"
  function price(v) {
    const t = s(v).replace(/[^\d.]/g, '');
    if (!t) return '';
    const n = Number(t);
    return Number.isInteger(n) ? n.toFixed(1) : String(n);
  }

  // "157490" → "157,490"; "198,000 км" → "198,000"
  function km(v) {
    const t = s(v).replace(/[^\d]/g, '');
    return t ? Number(t).toLocaleString('en-US') : '';
  }

  function preset(car) { return PRESETS[s(car.preset)] || {}; }
  function label(car) { return s(car.label) || preset(car).label || s(car.name).toUpperCase(); }
  function name(car) { return s(car.name) || preset(car).name || label(car); }
  function years(car) { return [s(car.year_made), s(car.year_import)].filter(Boolean).join('/'); }
  function hybrid(car) { return /hybrid|хайбрид|prius/i.test([car.engine, car.name, car.label, car.preset].join(' ')); }

  function statusLine(o) {
    if (o.status === 'arriving') return o.month ? `${o.month} САРД БУУНА` : 'ЗАМДАА ЯВАА';
    if (o.status === 'customs') return 'ГААЛИАС ШУУД';
    return 'УБ-Д БЭЛЭН';
  }

  function intro(car, o, many) {
    const what = many ? `${many} ширхэг ${name(car)}` : name(car);
    if (o.status === 'arriving') {
      return `Японоос орж ирэх ${what} ${o.month ? `ойролцоогоор ${o.month} сард` : 'удахгүй'} бууна.`;
    }
    if (o.status === 'customs') return `${what} гаалиас шууд, улсын дугаар аваагүй.`;
    return `${what} Улаанбаатарт бэлэн байна. Үзэж, туршиж болно.`;
  }

  function specLines(car, o) {
    const p = preset(car);
    const L = [];
    const frame = s(car.frame) || p.frame;
    L.push(['Загвар', name(car) + (frame ? `, ${frame}` : '')]);
    if (s(car.trim)) L.push(['Хувилбар', s(car.trim)]);
    if (s(car.year_made)) {
      let y = s(car.year_made);
      if (o.status === 'arriving') y += ` · Монголд буух: ${s(car.year_import) || new Date().getFullYear()}${o.month ? ` оны ${o.month} сар` : ''}`;
      else if (s(car.year_import)) y += ` · Орж ирсэн: ${s(car.year_import)}`;
      L.push(['Үйлдвэрлэсэн он', y]);
    }
    if (km(car.km)) L.push(['Явсан', `${km(car.km)} км`]);
    const eng = [s(car.engine) || p.engine, s(car.gearbox)].filter(Boolean).join(' · ');
    if (eng) L.push(['Мотор', eng]);
    if (s(car.drive)) L.push(['Хөтлөгч', s(car.drive)]);
    if (s(car.steering)) L.push(['Жолоо', s(car.steering)]);
    const seats = s(car.seats) || p.seats;
    if (seats) L.push(['Суудал', seats]);
    if (s(car.color)) L.push(['Өнгө', s(car.color)]);
    if (s(car.auction)) L.push(['Аукшн', s(car.auction)]);
    if (s(car.grade)) L.push(['Аукшны үнэлгээ', s(car.grade)]);
    return L;
  }

  function hashtags(cars, o) {
    const t = ['MidasMotors'];
    for (const c of cars) {
      for (const x of preset(c).tags || [label(c).replace(/[^\p{L}\p{N}]/gu, '')]) if (x && !t.includes(x)) t.push(x);
      if (hybrid(c) && !t.includes('Хайбрид')) t.push('Хайбрид');
    }
    if (o.status === 'arriving') {
      t.push('Захиалгаармашин');
      if (o.month) t.push(`${o.month}сардбуух`);
    }
    if (o.status === 'customs') t.push('Гаалиасшууд');
    if (o.loan) t.push('Банкбус');
    for (const x of s(o.tags).split(/[\s,]+/)) {
      const v = x.replace(/^#/, '');
      if (v && !t.includes(v)) t.push(v);
    }
    return t.map(x => '#' + x).join(' ');
  }

  function whyBlock(cars) {
    const custom = cars.flatMap(c => s(c.notes).split('\n').map(s).filter(Boolean));
    if (custom.length) return ['Онцлог', custom];
    const p = preset(cars[0]);
    if (p.why && cars.every(c => s(c.preset) === s(cars[0].preset))) return [p.whyTitle, p.why];
    return null;
  }

  function tailLines(o, many) {
    const out = [];
    if (o.status === 'arriving' || o.loan) {
      const terms = [...(o.status === 'arriving' ? PAYMENT : []), ...(o.loan ? [LOAN] : [])];
      out.push('💰 Төлбөрийн нөхцөл\n' + terms.map(x => '▪ ' + x).join('\n'));
    }
    const sheet = o.status === 'ready' ? 'Нэмэлт зураг, дэлгэрэнгүй мэдээллийг' : 'Аукшны хуудас болон нэмэлт зургийг';
    out.push(`${many ? 'Машин бүрийн ' + sheet.charAt(0).toLowerCase() + sheet.slice(1) : sheet} хүсвэл мессежээр илгээнэ.`);
    if (o.status === 'arriving') {
      out.push(`${o.month ? o.month + ' сард буухаас' : 'Буухаас'} өмнө урьдчилан захиалж, машинаа баталгаажуулах боломжтой. Мөн өөр загвар, өнгө, оноор захиалга авна.`);
    }
    return out;
  }

  function single(car, o) {
    const head = `${label(car)} · ${years(car)} · ${price(car.price)} сая₮`;
    const sub = [s(car.trim), s(car.color), statusLine(o)].filter(Boolean).join(' · ');
    const parts = [head + '\n' + sub];
    parts.push([intro(car, o), s(o.extra)].filter(Boolean).join(' '));
    const specs = specLines(car, o);
    if (price(car.price)) specs.push(['Үнэ', `${price(car.price)} сая₮`]);
    parts.push(specs.map(([k, v]) => `▪ ${k}: ${v}`).join('\n'));
    const why = whyBlock([car]);
    if (why) parts.push(why[0] + '\n' + why[1].map(x => '▪ ' + x).join('\n'));
    parts.push(...tailLines(o, false));
    parts.push(`📞 Утас: ${o.phone}`);
    parts.push(hashtags([car], o));

    const short = [
      `${label(car)} · ${years(car)} · ${price(car.price)} сая₮${o.status === 'arriving' && o.month ? ` · ${o.month} сард бууна` : ''}`,
      [km(car.km) && `${km(car.km)} км`, s(car.engine) || preset(car).engine, s(car.grade) && `Аукшн ${s(car.grade)}`, s(car.trim), s(car.color)].filter(Boolean).join(' · '),
      `Утас: ${o.phone}`,
    ];
    return { long: parts.join('\n\n'), short: short.join('\n') };
  }

  function multi(cars, o) {
    const sameModel = cars.every(c => label(c) === label(cars[0]));
    const prices = cars.map(c => price(c.price)).filter(Boolean);
    const title = o.title || (sameModel ? `${cars.length} ${label(cars[0])}` : `${cars.length} МАШИН`);
    const titleShort = o.title || (sameModel ? title : `${cars.length} машин`);
    const when = o.status === 'arriving' ? (o.month ? `${o.month} САРД БУУХ ` : 'ЗАМДАА ЯВАА ') : o.status === 'customs' ? 'ГААЛИАС ШУУД ' : 'БЭЛЭН ';
    const head = `🚗 MIDAS MOTORS · ${when}${title}${prices.length ? ' · ' + prices.join(' / ') + ' сая₮' : ''}`;
    const parts = [head];
    parts.push([sameModel ? intro(cars[0], o, cars.length) : intro({ name: `${cars.length} машин` }, o), s(o.extra)].filter(Boolean).join(' '));

    cars.forEach((c, i) => {
      const L = [`🚗 ${i + 1}. ${sameModel ? '' : label(c) + ' · '}${years(c)} · ${km(c.km) ? km(c.km) + ' км · ' : ''}${price(c.price)} сая₮`];
      const extra = specLines(c, o).filter(([k]) => !['Загвар', 'Үйлдвэрлэсэн он', 'Явсан', 'Суудал'].includes(k) || (k === 'Загвар' && !sameModel));
      for (const [k, v] of extra) L.push(`▪ ${k}: ${v}`);
      parts.push(L.join('\n'));
    });

    const why = whyBlock(cars);
    if (why) parts.push(why[0] + '\n' + why[1].map(x => '▪ ' + x).join('\n'));
    parts.push(...tailLines(o, true));
    parts.push(`📞 Утас: ${o.phone}`);
    parts.push(hashtags(cars, o));

    const short = [
      `${when.trim().charAt(0) + when.trim().slice(1).toLowerCase()} ${titleShort}`.replace(/\s+/g, ' '),
      ...cars.map((c, i) => `${i + 1}) ${[sameModel ? '' : label(c), years(c), km(c.km) && km(c.km) + ' км', s(c.trim), price(c.price) && price(c.price) + ' сая₮'].filter(Boolean).join(' · ')}`),
      `Утас: ${o.phone}`,
    ];
    return { long: parts.join('\n\n'), short: short.join('\n') };
  }

  function buildCaption(cars, opts) {
    const o = Object.assign({ status: 'arriving', month: '', phone: '9910-9653', loan: true, extra: '', tags: '', title: '' }, opts || {});
    o.month = s(o.month).replace(/\D/g, '');
    const list = (cars || []).filter(c => c && (s(c.name) || s(c.label) || s(c.preset)));
    if (!list.length) return { long: '', short: '' };
    const r = list.length === 1 ? single(list[0], o) : multi(list, o);
    return { long: r.long.replace(/\n{3,}/g, '\n\n').trim(), short: r.short.trim() };
  }

  // ---------- Постерын JSON → тайлбарын өгөгдөл ----------

  function presetFor(model, gen) {
    const k = (s(model) + s(gen)).toLowerCase().replace(/[^a-z0-9]/g, '');
    if (PRESETS[k]) return k;
    if (k === 'prius51' || k === 'prius50') return 'prius51';
    return '';
  }

  function statusFrom(entry) {
    const b = s(entry.badge_text).toUpperCase();
    const m = b.match(/(\d{1,2})\s*САРД/);
    if (m || /БУУНА|ЗАМДАА/.test(b)) return { status: 'arriving', month: m ? m[1] : '' };
    if (entry.badge === 'customs' || /ГААЛ/.test(b)) return { status: 'customs', month: '' };
    return { status: 'ready', month: '' };
  }

  function carFromPoster(c) {
    const specs = Object.fromEntries((c.specs || []).map(([k, v]) => [s(k), s(v)]));
    const p = presetFor(c.model, c.gen);
    return {
      preset: p,
      label: [s(c.model), s(c.gen)].filter(Boolean).join(' '),
      name: p ? '' : ['Toyota', s(c.model), s(c.gen)].filter(Boolean).join(' ').replace(/^Toyota (?!PRIUS|CAMRY)/, ''),
      trim: /^(Prius α|Hybrid)$/i.test(s(c.trim)) ? '' : s(c.trim),
      year_made: s(c.year_made), year_import: s(c.year_import),
      km: specs['Явсан'] || s(c.km), engine: specs['Мотор'] && specs['Мотор'] !== '—' ? specs['Мотор'] : '',
      drive: specs['Хөтлөгч'] && specs['Хөтлөгч'] !== '—' ? specs['Хөтлөгч'] : '',
      steering: specs['Жолоо'] && specs['Жолоо'] !== '—' ? specs['Жолоо'] : '',
      seats: specs['Суудал'] || '', grade: specs['Аукшн'] || '',
      color: s(c.color), price: s(c.price),
    };
  }

  function fromPosterEntry(entry) {
    const st = statusFrom(entry);
    const cars = entry.template === 'lineup' ? (entry.cars || []).map(carFromPoster) : [carFromPoster(entry)];
    const loan = !!s(entry.lease_title) || (entry.cars || []).some(c => c.tag === 'lease');
    const phone = /\d{4}-?\d{4}/.test(s(entry.phone)) ? s(entry.phone) : '9910-9653';
    return { cars, opts: { ...st, phone, loan: loan || st.status === 'arriving' } };
  }

  const api = { PRESETS, buildCaption, fromPosterEntry };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.MidasCaption = api;
})(typeof window !== 'undefined' ? window : globalThis);
