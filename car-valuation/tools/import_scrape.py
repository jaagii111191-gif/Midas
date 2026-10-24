# tools/scrape_export.js-ийн татсан файлыг data/ хавтсанд бусад огноотой ижил бүтэцтэй болгож задлана.
# Хэрэглэх: python tools/import_scrape.py unegui_toyota_2026-10-24.json
# Гаралт: data/unegui_toyota_<огноо>.json (raw, түлхүүр "D"), data/unegui_prius55_<огноо>.json,
#         data/prepped_<огноо>.json. Дараа нь: python tools/enrich.py <огноо>
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(path):
    src = json.load(open(path, encoding='utf-8'))
    d, raw, prep = src['date'], src['raw'], src['prepped']
    is55 = lambda r: r.get('slug') == 'Prius55'
    out = lambda name, obj: json.dump(obj, open(os.path.join(ROOT, 'data', name), 'w', encoding='utf-8'), ensure_ascii=False)
    out(f'unegui_toyota_{d}.json', {'exported': src['exported'], 'D_date': src['exported'], 'D': [r for r in raw if not is55(r)]})
    out(f'unegui_prius55_{d}.json', {'exported': src['exported'], 'raw': [r for r in raw if is55(r)], 'prepped': [r for r in prep if is55(r)]})
    out(f'prepped_{d}.json', [r for r in prep if not is55(r)])
    print(d, 'raw', len(raw), 'prepped', len(prep), 'Prius55', sum(map(is55, raw)))


if __name__ == '__main__':
    main(sys.argv[1])
