# Lambda сонголтыг олон санамсаргүй хуваалтаар шалгах, зарын нас (ID) шинжийг турших,
# зарагдсан (алга болсон) зарууд загвараас хямд байсан эсэхийг харах.
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import compare_and_refit as M

M.OLD, M.NEW = sys.argv[1], sys.argv[2]
old_raw, new_raw = M.load(M.OLD), M.load(M.NEW)
merged = list({**{r['u']: r for r in old_raw if r['price']}, **{r['u']: r for r in new_raw if r['price']}}.values())
adid = lambda r: int(r['u'].split('/')[2].split('_')[0])
ids = sorted(adid(r) for r in merged)
for r in old_raw + new_raw + merged:
    r['agerank'] = 1 - ids.index(adid(r)) / len(ids) if adid(r) in ids else 0   # 0 = хамгийн шинэ зар, 1 = хамгийн хуучин


def rep_cv(rows, lam, extra=False, reps=10, folds=5):
    base = M.build_cols(rows)
    if extra: base.append(('adage', 1, lambda r: r['agerank']))
    M.cache(rows, base)
    beta = M.fit(rows, base, lam)
    res = [math.log(r['price']) - M.pred(r, base, beta) for r in rows]
    sd = math.sqrt(sum(e * e for e in res) / len(res))
    clean = [r for r, e in zip(rows, res) if abs(e) < 3 * sd]
    cols = M.build_cols(clean)
    if extra: cols.append(('adage', 1, lambda r: r['agerank']))
    M.cache(clean, cols)
    out = []
    for s in range(reps):
        idx = list(range(len(clean))); random.Random(s).shuffle(idx)
        errs = []
        for k in range(folds):
            te = set(idx[k::folds])
            bb = M.fit([r for i, r in enumerate(clean) if i not in te], cols, lam)
            errs += [abs(math.exp(M.pred(clean[i], cols, bb)) / clean[i]['price'] - 1) for i in te]
        out.append(M.med(errs))
    coef = dict(zip([c[0] for c in cols], M.fit(clean, cols, lam)))
    return sum(out) / len(out), min(out), max(out), coef


rows = M.model_rows(M.base_filter(merged, True))
result = {}
for lam in [0.25, 0.5, 1, 2]:
    a, lo, hi, _ = rep_cv(rows, lam)
    result[f'lam{lam}'] = [round(a, 4), round(lo, 4), round(hi, 4)]
a, lo, hi, coef = rep_cv(rows, 0.5, extra=True)
result['lam0.5+adage'] = [round(a, 4), round(lo, 4), round(hi, 4), 'adage coef', round(coef['adage'], 4)]

# Бүх зар (дугаартай орсон) хүрээнд мөн шалгах
rows_all = M.model_rows(M.base_filter(merged, False))
for lam in [0.5, 1, 2]:
    a, lo, hi, _ = rep_cv(rows_all, lam, reps=3)
    result[f'ALL_lam{lam}'] = [round(a, 4), round(lo, 4), round(hi, 4), len(rows_all)]

# Алга болсон зарууд (зарагдсан эсвэл устгасан) загвараас хямд байсан уу?
_, _, _, coef_all = rep_cv(rows_all, 1, reps=1)
new_u = {r['u'] for r in new_raw}
old_rows = M.model_rows(M.base_filter(old_raw, False))
gone = [math.log(r['price']) - M.pred_coef(r, coef_all) for r in old_rows if r['u'] not in new_u]
stay = [math.log(r['price']) - M.pred_coef(r, coef_all) for r in old_rows if r['u'] in new_u]
result['gone_vs_model_median_pct'] = round(math.exp(M.med(gone)) - 1, 4)
result['stay_vs_model_median_pct'] = round(math.exp(M.med(stay)) - 1, 4)
result['gone_n'], result['stay_n'] = len(gone), len(stay)
result['gone_share_cheap_10pct'] = round(sum(e < -0.105 for e in gone) / len(gone), 3)
result['stay_share_cheap_10pct'] = round(sum(e < -0.105 for e in stay) / len(stay), 3)
print(json.dumps(result, ensure_ascii=False, indent=1))
with open(os.path.join(M.ROOT, 'data', f'robustness_{M.OLD}_{M.NEW}.json'), 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
