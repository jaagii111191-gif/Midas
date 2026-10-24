# prepped_<огноо>.json-д нэмэлт шинж нэмнэ (2026-10-11-нээс):
#  - cgen: Camry-ийн үе (50 / 70 / None). 2018+ = 70, 2016 хүртэл = 50, 2017 онд хоёр үе зэрэг гарсан
#          тул тайлбар/гарчгаас ("Camry 70", "AXVH70", "сер2" г.м.) уншина. Олдохгүй бол None.
#  - is55: Prius 55 (ZVW55, Prius 50-ийн E-Four 4WD хувилбар).
#  - Prius55 ангиллын зарыг (unegui_prius55_<огноо>.json) тухайн огнооны prepped файлд нэмнэ.
# Хэрэглэх: python tools/enrich.py 2026-10-01 2026-10-04 2026-10-11
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAWKEY = {'2026-10-01': 'D2', '2026-10-04': 'D3', '2026-10-11': 'D4'}

C70 = re.compile(r'(camry|камри|xv|axvh|asv|avv)[\s\-_#.]*7\d(?!\d)|(?<!\d)7\d[\s\-_]*(camry|камри|series|цуврал)|camry_?70|dynamic\s*force|\btnga\b', re.I)
C50 = re.compile(r'(camry|камри|xv|avv|asv|acv)[\s\-_#.]*5\d(?!\d)|(?<!\d)5\d[\s\-_]*(camry|камри|series|цуврал)|\b(ser|сер)[\s\-]*2\b|сер2|ser2', re.I)


MON = re.compile(r'2017\s*(?:он[ыи]?|оны|on[iy]?)?\s*[/.\-]?\s*(\d{1,2})\s*(?:сар|sar|-р)|2017\s*[/.]\s*(\d{1,2})(?!\d)', re.I)


def cgen(made, text, grade=''):
    """text = зөвхөн тайлбар (гарчигт "2017/2026" байдаг тул сар хайхад оруулахгүй)."""
    if made >= 2018: return 70
    if made <= 2016: return 50
    a, b = bool(C70.search(text)), bool(C50.search(text))
    if a != b: return 70 if a else 50
    if grade in ('ws', 'wsl'): return 70            # WS зөвхөн 70-д бий
    m = MON.search(text)                             # Camry 70 Японд 2017.07-д гарсан
    if m:
        mo = int(m.group(1) or m.group(2))
        if 8 <= mo <= 12: return 70
        if 1 <= mo <= 6: return 50
    return None


def main(dates):
    for d in dates:
        p = os.path.join(ROOT, 'data', f'prepped_{d}.json')
        rows = json.load(open(p, encoding='utf-8'))
        raw = json.load(open(os.path.join(ROOT, 'data', f'unegui_toyota_{d}.json'), encoding='utf-8'))[RAWKEY[d]]
        txt = {r['u']: r.get('desc') or '' for r in raw}
        p55 = os.path.join(ROOT, 'data', f'unegui_prius55_{d}.json')
        if os.path.exists(p55):
            extra = json.load(open(p55, encoding='utf-8'))
            have = {r['u'] for r in rows}
            rows += [r for r in extra['prepped'] if r['u'] not in have]
            txt.update({r['u']: r.get('desc') or '' for r in extra['raw']})
        n = {50: 0, 70: 0, None: 0}
        for r in rows:
            r.setdefault('is55', r.get('slug') == 'Prius55')
            if r['fam'] == 'camry':
                t = txt.get(r['u'], ''); c = t.rfind(str(r['price']) + ' сая'); t = t[:c] if c > 0 else t
                r['cgen'] = cgen(r['made'], t, r['grade'])
                if r['made'] == 2017: n[r['cgen']] += 1
            else:
                r['cgen'] = None
        json.dump(rows, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
        print(d, 'rows', len(rows), 'Prius55', sum(r['is55'] for r in rows), 'Camry 2017 үе:', n)


if __name__ == '__main__':
    main(sys.argv[1:])
