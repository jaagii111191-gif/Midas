// unegui.mn-ээс татсан түүхий зарын өгөгдлийг JSON файл болгон татах.
// Хэрэглэх: Chrome-оор https://www.unegui.mn нээгээд F12 → Console дээр энэ файлыг бүтнээр нь буулгаж Enter дарна.
// "unegui_toyota_YYYY-MM-DD.json" файл Downloads хавтсанд бууна.
// Түүнийг E:\tttt\car-valuation\data\ рүү зөөнө.
// Өгөгдөл: "D2" = бүх талбартай 2,037 зар (2026-10-01), "D" = өмнөх татлага.

(async () => {
  const get = k => new Promise((res, rej) => {
    const r = indexedDB.open('carval', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('kv');
    r.onsuccess = () => { const q = r.result.transaction('kv').objectStore('kv').get(k); q.onsuccess = () => res(q.result); q.onerror = rej; };
    r.onerror = rej;
  });
  const data = { exported: new Date().toISOString(), D2_date: await get('D2_date'), D2: await get('D2'), D_date: await get('D_date'), D: await get('D') };
  if (!data.D2 && !data.D) { console.log('Өгөгдөл олдсонгүй. Энэ хөтөч дээр татлага хийгээгүй эсвэл цэвэрлэгдсэн байна.'); return; }
  const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'unegui_toyota_' + new Date().toISOString().slice(0, 10) + '.json';
  a.click();
  console.log('Татлаа:', (data.D2 || []).length, 'зар (D2),', (data.D || []).length, 'зар (D)');
})();
