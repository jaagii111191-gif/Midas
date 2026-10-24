# Camry-ийн үе, Prius 55 шинж нэмэхэд нарийвчлал сайжирсан эсэхийг давтан CV-ээр шалгах.
import json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import compare_and_refit as M
import compare_multi as CM

DATES = ['2026-10-01', '2026-10-04', '2026-10-11']
mg = {}
for d in DATES:
    for r in M.load(d):
        if r['price']: mg[r['u']] = r
rows_all = M.model_rows(M.base_filter(list(mg.values()), True))
rows_no55 = [r for r in rows_all if not r.get('is55')]
out = {}
for name, gen, rows in [('v7 (шинжгүй, 55-гүй)', False, rows_no55), ('үе + is55 (55-гүй)', True, rows_no55), ('үе + is55 (55-тай)', True, rows_all)]:
    M.GEN = gen
    t = CM.rep_cv([dict(r) for r in rows], 1)
    cam = [r for r in t['clean'] if r['fam'] == 'camry']
    coef = dict(zip([c[0] for c in t['cols']], t['beta']))
    out[name] = {'n': len(t['clean']), 'mape': round(t['mape'], 4), 'range': [round(t['lo'], 4), round(t['hi'], 4)], 'by_fam': t['by_fam'],
                 'cam70': round(math.exp(coef.get('cam70', 0)) - 1, 3), 'cam17unk': round(math.exp(coef.get('cam17unk', 0)) - 1, 3),
                 'is55': round(math.exp(coef.get('is55', 0)) - 1, 3), 'camry_n': len(cam)}
print(json.dumps(out, ensure_ascii=False, indent=1))
