---
name: midas-poster
description: Midas Motors-ын машины зарын постер (1080×1350 PNG) гаргана. 1000mashin.mn-ийн зарын холбоосоос нэг машины олон зурагтай постер, хэд хэдэн холбоосоос нэг постерт олон машин, эсвэл JSON өгөгдлөөс постер гаргана. Use when the user asks for a Midas poster, "постер гарга", "зар хий", or pastes a 1000mashin.mn/car-view link.
---

# Midas Motors постер гаргах

Репозиторийн үндсэн хавтсаас `npm run poster -- …` командыг ажиллуулна. Командын бүх сонголт: `npm run poster -- help`.

1. `node_modules/` байхгүй бол эхлээд `npm install` хийнэ.
2. Хүсэлтээс командаа сонгоно:
   - Нэг холбоос → `npm run poster -- url <холбоос>` (олон зурагтай T7). «Нэг зурагтай» гэвэл `--t1` нэм.
   - 2–6 холбоос, «нэг постерт» гэвэл → `npm run poster -- lineup <холбоос> <холбоос> …` (T8).
   - JSON файл → `npm run poster -- render <файл>`.
   - Шошго хэлсэн бол `--badge "ГААЛИАС ШУУД" --badge-type customs` (бусад төрөл: new, lease, drop, out).
   - Утас, хаяг хэлсэн бол `--phone`, `--address`. Байнгын утгыг `data/midas-config.json`-д бичнэ.
3. Хөтөч асахгүй бол (cloud орчинд): `CHROMIUM_PATH=/opt/pw-browsers/chromium` тохируул. HTTPS прокситой сүлжээнд зураг ачаалагдахгүй бол `IGNORE_HTTPS_ERRORS=1` нэм.
4. Командын гаргасан `reports/midas-posters/<id>.png` файлыг нээж шалга. Дараа нь хэрэглэгчид үзүүл.
5. Зурган дээр Монголын улсын дугаар тод харагдаж байвал хэлээрэй. Стандартаар дугаарыг бүдгэрүүлэх ёстой бөгөөд энэ хэрэгсэл үүнийг автоматаар хийдэггүй.

Үүссэн өгөгдөл `data/generated/<id>.json`-д хадгалагдана. Үнэ, шошго, зургийн дараалал, тайралт (`pos`, `scale`) зэргийг засах хүсэлт ирвэл тэр файлыг засаад `npm run poster -- render data/generated/<id>.json` ажиллуулна.
