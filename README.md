# Midas Motors

Midas Motors-ын машины зарын постер, Facebook тайлбар, зах зээлийн судалгааны репозитори.

## Хавтасны бүтэц

| Хавтас | Зориулалт |
|---|---|
| `templates/midas-motors/` | Постерын HTML загварууд, фонт, лого |
| `bin/` | `midas-poster` терминалын хэрэгсэл |
| `data/` | Машины мэдээлэл (`midas-*.json`), зураг (`midas-photos/`), unegui.mn-ийн зарын өгөгдөл |
| `reports/` | Бэлэн постерууд (`midas-posters/`) ба зах зээлийн судалгааны тайлангууд |
| `scripts/` | unegui.mn-ээс зар татах, шинжлэх скриптүүд (Python, JS) |

## Судалгааны тайлангууд

- [Авто зах зээлийн судалгаа (2026-10)](reports/avto-zah-zeel-sudalgaa-2026-10.md)
- [unegui.mn үнийн харьцуулалт ба зах зээлийн багтаамж (2026-10)](reports/unegui-une-haritsuulalt-ba-zah-zeeliin-bagtaamj-2026-10.md)

## Midas Motors постерыг терминалаас гаргах

Анх нэг удаа (Node.js 18+ хэрэгтэй):

```
npm run setup
```

Дараа нь:

```
npm run poster -- url https://www.1000mashin.mn/car-view/11918/x                  # нэг машин, олон зурагтай
npm run poster -- url <холбоос> --badge "ГААЛИАС ШУУД" --badge-type customs          # шошготой
npm run poster -- lineup <холбоос1> <холбоос2> <холбоос3>                          # нэг постерт олон машин
npm run poster -- render data/midas-examples-1000mashin.json                       # JSON файлаас
npm run poster -- demo                                                             # загваруудын жишээ
npm run poster -- help                                                             # бүх сонголт
```

Постерууд `reports/midas-posters/` хавтсанд PNG болж гарна. Утас, хаягаа `data/midas-config.json`-д нэг удаа бичнэ.
`url`, `lineup` командууд үүсгэсэн өгөгдлөө `data/generated/` хавтсанд хадгалдаг. Түүнийг засаад `render` командаар дахин гаргана.

Claude Code дээр `/midas-poster <холбоос>` гэж бичээд ч гаргуулж болно.

## Постерын тайлбар (Facebook caption)

`url`, `lineup`, `render` командууд постер бүрийн хажууд `<id>-caption.txt` тайлбар бичнэ: урт Facebook тайлбар, доор нь story, Marketplace-д зориулсан богино хувилбар. Утас, төлбөрийн нөхцөл (30% урьдчилгаа), «N сард бууна» гэдгийг постерын шошгоноос авна.

```
npm run poster -- caption data/midas-prius41-dec.json        # зөвхөн тайлбар, хөтөч хэрэггүй
```

Вэбээр бичих бол `templates/midas-motors/caption.html` файлыг хөтчөөр нээнэ (онлайн хувилбар: https://claude.ai/artifact/B5KkZ76i4HKVVn7TfFy2pU). Машины мэдээллээ бөглөхөд тайлбар шууд гарч, «Хуулах» товчоор авна. Постерын JSON-оо хуулж тавиад бөглүүлж бас болно.

Тайлбарын дүрэм `templates/midas-motors/caption.js`-д байгаа бөгөөд вэб хуудас, терминал хоёул үүнийг ашиглана. Prius α-д «Яагаад Prius α гэж?» хэсэг автоматаар орно. Бусад загварт «Онцлог» талбарт өөрөө бичнэ.
