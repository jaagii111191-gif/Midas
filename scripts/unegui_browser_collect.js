// unegui.mn-ээс Toyota 8 загварын зарыг ХӨТӨЧ ДЭЭРЭЭС цуглуулж CSV татна.
//
// Хэрэглэх заавар:
//   1. Chrome/Edge дээр https://www.unegui.mn нээнэ.
//   2. F12 (эсвэл Ctrl+Shift+J) дарж Console хэсгийг нээнэ.
//   3. Энэ файлын бүх агуулгыг хуулж Console-д буулгаад Enter дарна.
//      (Chrome анх удаа "allow pasting" гэж бичихийг шаардаж магадгүй.)
//   4. Дуустал хүлээнэ (15–30 мин). Явц Console-д харагдана.
//      Дуусахад unegui_raw_2026-10.csv файл автоматаар татагдана.
//   5. Тэр CSV файлыг Claude-д илгээнэ.
//
// Ангиллын хуудаснаас бүх зарын гарчиг, үнэ, он/орсон оныг авна. Дэлгэрэнгүй хуудсыг
// (гүйлт, хөдөлгүүр, хөтлөгч, тайлбар) зөвхөн DETAIL_MIN_IMPORT_YEAR-аас хойш орж
// ирсэн машинд татна.
(async () => {
  const BASE = "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/toyota/";
  const CATEGORIES = {
    "Prius 40": "prius-40/",
    "Prius 41": "prius-41/",
    "Prius 50": "50/",
    "Prius 55": "Prius55/",
    "Prius 60": "prius-60/",
    "Camry": "camry/",
    "Crown": "crown/",
    "Harrier": "harrier/",
  };
  const MAX_PAGES = 15;               // ангилал бүрээс хамгийн ихдээ хэдэн хуудас
  const DETAIL_MIN_IMPORT_YEAR = 2025; // үүнээс хойш орж ирсэн бол дэлгэрэнгүйг татна
  const DELAY_MS = 1000;              // сайтад ачаалал өгөхгүйн тулд хүсэлт хооронд 1 сек

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const getDoc = async (url) => {
    const resp = await fetch(url, { credentials: "omit" });
    if (resp.ok === false) throw new Error(`HTTP ${resp.status} ${url}`);
    return new DOMParser().parseFromString(await resp.text(), "text/html");
  };
  const clean = (s) => (s || "").replace(/\s+/g, " ").trim();
  const YEARS_RE = /(\d{4})\s*\/\s*(\d{4})/;
  const PRICE_RE = /([\d][\d\s.,]*)\s*(сая)?\s*₮/;

  function parsePrice(text) {
    const m = PRICE_RE.exec(text || "");
    if (!m) return "";
    const n = parseFloat(m[1].replace(/\s/g, "").replace(/,/g, ""));
    if (!isFinite(n)) return "";
    return m[2] ? n : +(n / 1e6).toFixed(3);
  }

  // Ангиллын хуудаснаас зарын картуудыг гарчиг + үнэтэй нь салгаж авна.
  const advId = (a) => (/\/adv\/(\d+)/.exec(a.getAttribute("href") || "") || [])[1];
  const isCar = (text) => YEARS_RE.test(text) && PRICE_RE.test(text);

  function cardsFrom(doc) {
    const out = new Map();
    for (const a of doc.querySelectorAll('a[href*="/adv/"]')) {
      if (!advId(a)) continue;
      const href = new URL(a.getAttribute("href"), location.origin).href.split("?")[0];
      if (out.has(href)) continue;
      // Зөвхөн энэ зарын картын хүрээнд дээшилнэ: өөр зарын холбоос агуулсан эцэг
      // элементэд хүрмэгц зогсоно (хөрш картын он/үнэ холилдохоос сэргийлнэ).
      let el = a, text = clean(a.textContent);
      while (!isCar(text) && el.parentElement) {
        const ids = new Set([...el.parentElement.querySelectorAll('a[href*="/adv/"]')].map(advId).filter(Boolean));
        if (ids.size > 1) break;
        el = el.parentElement;
        text = clean(el.textContent);
      }
      if (isCar(text)) out.set(href, text); // үгүй бол машины зар биш (сэлбэг г.м.)
    }
    return out;
  }

  // Дэлгэрэнгүй хуудасны "Түлхүүр: утга" хосуудыг HTML бүтцээс үл хамааран түүнэ.
  function charsFrom(doc) {
    const chars = {};
    for (const li of doc.querySelectorAll("li, tr, dl > div")) {
      const kids = [...li.children].filter((c) => clean(c.textContent));
      if (kids.length < 2) continue;
      const key = clean(kids[0].textContent);
      if (!key.endsWith(":") || key.length > 40) continue;
      chars[key.slice(0, -1)] = clean(kids.slice(1).map((k) => k.textContent).join(" "));
    }
    for (const dt of doc.querySelectorAll("dt")) {
      const dd = dt.nextElementSibling;
      if (dd && dd.tagName === "DD") chars[clean(dt.textContent).replace(/:$/, "")] = clean(dd.textContent);
    }
    return chars;
  }

  function descriptionFrom(doc) {
    const el = doc.querySelector('[class*="description"], [itemprop="description"]');
    return clean(el && el.textContent).slice(0, 2000);
  }

  const rows = [];
  const seen = new Set();
  for (const [model, slug] of Object.entries(CATEGORIES)) {
    for (let page = 1; page <= MAX_PAGES; page++) {
      let cards;
      try {
        cards = cardsFrom(await getDoc(`${BASE}${slug}?page=${page}`));
      } catch (e) {
        console.warn(model, page, e);
        break;
      }
      const fresh = [...cards].filter(([url]) => !seen.has(url));
      if (!fresh.length) break;
      for (const [url, cardText] of fresh) {
        seen.add(url);
        const y = YEARS_RE.exec(cardText);
        const row = {
          model,
          title: cardText.slice(0, 200),
          mfg_year: y ? y[1] : "",
          import_year: y ? y[2] : "",
          price_mnt_m: parsePrice(cardText),
          url,
        };
        if (y && +y[2] >= DETAIL_MIN_IMPORT_YEAR) {
          await sleep(DELAY_MS);
          try {
            const doc = await getDoc(url);
            const chars = charsFrom(doc);
            row.title = clean(doc.querySelector("h1") && doc.querySelector("h1").textContent) || row.title;
            const priceEl = doc.querySelector('[class*="price"]');
            row.price_mnt_m = parsePrice(priceEl && priceEl.textContent) || row.price_mnt_m;
            row.mileage = chars["Явсан"] || chars["Гүйлт"] || "";
            row.engine = chars["Мотор багтаамж"] || "";
            row.fuel = chars["Хөдөлгүүр"] || "";
            row.drive = chars["Хөтлөгч"] || "";
            row.description = descriptionFrom(doc);
            for (const [k, v] of Object.entries(chars)) row[`char:${k}`] = v;
          } catch (e) {
            console.warn("detail", url, e);
          }
        }
        rows.push(row);
      }
      console.log(`${model}: хуудас ${page}, нийт ${rows.length} зар`);
      await sleep(DELAY_MS);
    }
  }

  const cols = [...new Set(rows.flatMap(Object.keys))];
  const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = "﻿" + [cols.map(esc).join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\n");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  a.download = "unegui_raw_2026-10.csv";
  document.body.appendChild(a);
  a.click();
  console.log(`Дууслаа: ${rows.length} зар → unegui_raw_2026-10.csv`);
})();
