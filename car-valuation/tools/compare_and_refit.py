# Хоёр татлагын үнийг харьцуулж, үнэлгээний загварыг нэгтгэсэн өгөгдлөөр дахин сургана.
# Оролт: data/prepped_<огноо>.json (хөтөч дээр scrape_and_fit.js-ийн prep()-ээр гаргасан мөрүүд).
# Хэрэглэх: python tools/compare_and_refit.py 2026-10-01 2026-10-04
import json, math, os, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD, NEW = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else (None, None)
NOW = 2026
GEN = True   # False = v7 хүртэлх баганууд
FAMS =['alpha', 'p50', 'camry', 'harrier']
GRADES = {
    'alpha': ['gs', 'gtour', 'stour', 'tune', 'lsel', 'g', 's', 'l'],
    'p50': ['apt', 'aprem', 'atour', 'stour', 'ssafe', 'a', 'e', 's'],
    'camry': ['wsl', 'ws', 'gl', 'g', 'x'],
    'harrier': ['zl', 'z', 'gl', 'pmetal', 'progress', 'padv', 'premium', 'elegance', 'grand', 'airs', 'lpkg', 'g', 's'],
}
BASEG = {'alpha': 's', 'p50': 's', 'camry': 'g', 'harrier': 'premium'}
FAM_MN = {'alpha': 'Prius α (40/41)', 'p50': 'Prius 50/51', 'camry': 'Camry', 'harrier': 'Harrier'}


def load(date):
    with open(os.path.join(ROOT, 'data', f'prepped_{date}.json'), encoding='utf-8') as f:
        return json.load(f)


# ---------- Загварын баганууд (scrape_and_fit.js buildCols-той ижил) ----------
def build_cols(rows, inner=False, period=False):
    cols = []
    add = lambda k, pen, v: cols.append((k, pen, v))
    for f in FAMS:
        add('int_' + f, 0, lambda r, f=f: 1 if r['fam'] == f else 0)
        add('yr_' + f, 0, lambda r, f=f: r['made'] - 2015 if r['fam'] == f else 0)
        add('km_' + f, .5, lambda r, f=f: math.log(min(max(r['km'] or 150000, 10000), 400000) / 150000) if r['fam'] == f else 0)
        for y in sorted({r['made'] for r in rows if r['fam'] == f}):
            add(f'y_{f}_{y}', 3, lambda r, f=f, y=y: 1 if r['fam'] == f and r['made'] == y else 0)
        for g in GRADES[f] + ['']:
            if g != BASEG[f]:
                add(f'g_{f}_{g or "unk"}', .3, lambda r, f=f, g=g: 1 if r['fam'] == f and r['grade'] == g else 0)
        add('lhd_' + f, .5, lambda r, f=f: 1 if r['fam'] == f and r['wheel'] == 'Зөв' else 0)
        add('ymnf_' + f, 2, lambda r, f=f: min(r['ymn'], 8) if r['fam'] == f and not r['fresh'] else 0)
        if period:
            add('new_' + f, .01, lambda r, f=f: 1 if r['fam'] == f and r.get('_new') else 0)
    add('gas_camry', 1, lambda r: 1 if r['fam'] == 'camry' and r['gas'] else 0)
    add('gas_harrier', 1, lambda r: 1 if r['fam'] == 'harrier' and r['gas'] else 0)
    add('cc35_harrier', 1, lambda r: 1 if r['fam'] == 'harrier' and r['cc35'] else 0)
    add('cc20_harrier', 1, lambda r: 1 if r['fam'] == 'harrier' and r['cc20'] else 0)
    for b in ['ub', 'roof', 'jbl', 'cam360', 'hud', 'leather', 'radar', 'is40', 'is51', 'awd',
              'winter', 'led', 'modellista', 'battery', 'dealer', 'urgent', 'nego', 'swap']:
        add(b, 1, lambda r, b=b: 1 if r[b] else 0)
    for c in ['pearl', 'white', 'black', 'gray', 'red', 'blue', 'brown']:
        add('c_' + c, .3, lambda r, c=c: 1 if r['colg'] == c else 0)
    for v in ['ББСБ лизингтэй', 'Банкны лизингтэй', 'Хувь лизингтэй']:
        add('lease=' + v, .5, lambda r, v=v: 1 if r['lease'] == v else 0)
    for v in ['withplate', 'z00']:
        add('cond=' + v, .5, lambda r, v=v: 1 if r['ck'] == v else 0)
    if inner:
        for v in ['Саарал', 'Бусад', 'Шаргал', 'Цагаан шар', 'Бор']:
            add('inner=' + v, .5, lambda r, v=v: 1 if r['inner'] == v else 0)
    add('hasScore', 1, lambda r: 1 if r['score'] else 0)
    add('score', 1, lambda r: r['score'] - 4 if r['score'] else 0)
    for a, b in [(1, 1), (2, 2), (3, 3), (4, 5), (6, 99)]:
        add(f'ymn_{a}', 1, lambda r, a=a, b=b: 1 if not r['fresh'] and a <= r['ymn'] <= b else 0)
    add('plated0', 1, lambda r: 1 if not r['fresh'] and r['ymn'] == 0 else 0)
    add('cc24_camry', 1, lambda r: 1 if r['fam'] == 'camry' and (r['cc'] or '').startswith('2.4') else 0)
    if GEN:   # v8: Camry-ийн үе (tools/enrich.py-ийн cgen), Prius 55
        add('cam70', .3, lambda r: 1 if r['fam'] == 'camry' and r.get('cgen') == 70 else 0)
        add('cam17unk', .3, lambda r: 1 if r['fam'] == 'camry' and r['made'] == 2017 and r.get('cgen') is None else 0)
        add('is55', 1, lambda r: 1 if r.get('is55') else 0)
    add('kmpy', 1, lambda r: (min(r['km'] / max(1, NOW - r['made']) / 20000, 3) - 1) if r['km'] else 0)
    add('lowkm', 1, lambda r: 1 if r['km'] and r['km'] < 5000 else 0)
    return cols


def solve(A, b):
    n = len(b)
    for i in range(n):
        p = max(range(i, n), key=lambda j: abs(A[j][i]))
        A[i], A[p] = A[p], A[i]; b[i], b[p] = b[p], b[i]
        d = A[i][i] or 1e-9
        for j in range(i + 1, n):
            f = A[j][i] / d
            if not f: continue
            Ai, Aj = A[i], A[j]
            for k in range(i, n): Aj[k] -= f * Ai[k]
            b[j] -= f * b[i]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = b[i] - sum(A[i][k] * x[k] for k in range(i + 1, n))
        x[i] = s / (A[i][i] or 1e-9)
    return x


def feats(r, cols):
    return [(i, v) for i, (_, _, fn) in enumerate(cols) if (v := fn(r))]


def fit(rows, cols, lam=1.0):
    p = len(cols)
    A = [[0.0] * p for _ in range(p)]; b = [0.0] * p
    for r in rows:
        x = r['_x'] if '_x' in r and r['_xc'] is cols else feats(r, cols)
        y = math.log(r['price'])
        for i, xi in x:
            b[i] += xi * y
            Ai = A[i]
            for j, xj in x: Ai[j] += xi * xj
    for i, (_, pen, _) in enumerate(cols): A[i][i] += lam * pen + 1e-6
    return solve(A, b)


def cache(rows, cols):
    for r in rows: r['_x'] = feats(r, cols); r['_xc'] = cols


def pred(r, cols, beta):
    x = r['_x'] if r.get('_xc') is cols else feats(r, cols)
    return sum(beta[i] * v for i, v in x)


def pred_coef(r, coef):
    """Хадгалсан коэффициентээр (жишээ нь v5) үнэлэх."""
    cols = build_cols([r])
    return sum(coef.get(k, 0) * fn(r) for k, _, fn in cols)


med = lambda v: sorted(v)[len(v) // 2] if v else None
q = lambda v, f: sorted(v)[int(f * (len(v) - 1))]


def base_filter(rows, fresh_only):
    seen, out = set(), []
    for r in rows:
        if not r['price'] or r['u'] in seen: continue
        seen.add(r['u'])
        if not (2003 <= r['made'] <= NOW and 4 <= r['price'] <= 250): continue
        if fresh_only and not (r['ck'] == 'fresh' and r['imp'] == NOW): continue
        out.append(r)
    return out


def model_rows(rows):
    dk, out = set(), []
    for r in rows:
        k = (r['fam'], r['made'], r['imp'], r['km'], r['color'], r['fresh'])
        if k in dk: continue
        dk.add(k)
        if (r['km'] or 0) > 450000 or r['impBad']: continue
        out.append(r)
    return out


def clean_and_cv(rows, lam=1.0, inner=False, period=False, folds=5):
    cols = build_cols(rows, inner, period); cache(rows, cols)
    beta = fit(rows, cols, lam)
    res = [math.log(r['price']) - pred(r, cols, beta) for r in rows]
    sd = math.sqrt(sum(e * e for e in res) / len(res))
    clean = [r for r, e in zip(rows, res) if abs(e) < 3 * sd]
    cols = build_cols(clean, inner, period); cache(clean, cols)
    idx = sorted(range(len(clean)), key=lambda i: (i * 2654435761) % 997)
    errs, fam_err = [], {}
    for k in range(folds):
        te = {i for j, i in enumerate(idx) if j % folds == k}
        bb = fit([r for i, r in enumerate(clean) if i not in te], cols, lam)
        for i in te:
            e = abs(math.exp(pred(clean[i], cols, bb)) / clean[i]['price'] - 1)
            errs.append(e); fam_err.setdefault(clean[i]['fam'], []).append(e)
    beta = fit(clean, cols, lam)
    return dict(clean=clean, cols=cols, beta=beta, mape=med(errs), within10=sum(e < .1 for e in errs) / len(errs),
                by_fam={f: round(med(v), 4) for f, v in fam_err.items()})


def main():
    old_raw, new_raw = load(OLD), load(NEW)
    old_u = {r['u']: r for r in old_raw if r['price']}
    new_u = {r['u']: r for r in new_raw if r['price']}
    out = {'old_date': OLD, 'new_date': NEW, 'counts': {'old': len(old_u), 'new': len(new_u)}}

    # ---------- 1. Ижил зарын үнийн өөрчлөлт ----------
    same = [(old_u[u], new_u[u]) for u in old_u.keys() & new_u.keys()]
    gone = [old_u[u] for u in old_u.keys() - new_u.keys()]
    fresh_new = [new_u[u] for u in new_u.keys() - old_u.keys()]
    rep = {'same': len(same), 'gone': len(gone), 'added': len(fresh_new), 'by_fam': {}}
    for f in FAMS + ['all']:
        pairs = [(a, b) for a, b in same if f == 'all' or a['fam'] == f]
        ch = [b['price'] / a['price'] - 1 for a, b in pairs]
        moved = [c for c in ch if abs(c) > 1e-9]
        rep['by_fam'][f] = {
            'n': len(pairs), 'up': sum(c > 1e-9 for c in ch), 'down': sum(c < -1e-9 for c in ch),
            'unchanged': sum(abs(c) <= 1e-9 for c in ch),
            'mean_change_all': round(statistics.mean(ch), 4) if ch else None,
            'median_change_moved': round(med(moved), 4) if moved else None,
            'gone': sum(1 for g in gone if f == 'all' or g['fam'] == f),
            'added': sum(1 for g in fresh_new if f == 'all' or g['fam'] == f),
            'median_price_old': med([a['price'] for a in old_u.values() if f == 'all' or a['fam'] == f]),
            'median_price_new': med([a['price'] for a in new_u.values() if f == 'all' or a['fam'] == f]),
            'median_price_gone': med([g['price'] for g in gone if f == 'all' or g['fam'] == f]),
            'median_price_added': med([g['price'] for g in fresh_new if f == 'all' or g['fam'] == f]),
        }
    big = sorted(((b['price'] / a['price'] - 1, a, b) for a, b in same if a['price'] != b['price']), key=lambda t: t[0])
    rep['biggest_cuts'] = [{'u': a['u'], 'old': a['price'], 'new': b['price'], 'pct': round(c, 3)} for c, a, b in big[:8]]
    rep['biggest_raises'] = [{'u': a['u'], 'old': a['price'], 'new': b['price'], 'pct': round(c, 3)} for c, a, b in big[-8:][::-1]]
    out['same_listing'] = rep

    # ---------- 2. v5-ийн урагшлах тест: 10-01-ний дараа гарсан шинэ зарууд ----------
    with open(os.path.join(ROOT, 'models', 'model_2026-10-01_v5_2026fresh.json'), encoding='utf-8') as f:
        v5 = json.load(f)
    fwd = model_rows(base_filter(fresh_new, True))
    fwd_res = [(r, math.log(r['price']) - pred_coef(r, v5['coef'])) for r in fwd]
    out['v5_forward'] = {
        'n': len(fwd_res),
        'mape': round(med([abs(math.exp(-e) - 1) for _, e in fwd_res]), 4) if fwd_res else None,
        'within10': round(sum(abs(math.exp(-e) - 1) < .1 for _, e in fwd_res) / len(fwd_res), 3) if fwd_res else None,
        'median_resid_pct': round(math.exp(med([e for _, e in fwd_res])) - 1, 4) if fwd_res else None,
        'by_fam': {f: {'n': len(v), 'median_resid_pct': round(math.exp(med(v)) - 1, 4)}
                   for f in FAMS if (v := [e for r, e in fwd_res if r['fam'] == f])},
    }
    # v5-ыг одоо байгаа бүх "шинэ" (fresh) зар дээр
    allf = model_rows(base_filter(new_raw, True))
    allf_res = [math.log(r['price']) - pred_coef(r, v5['coef']) for r in allf]
    out['v5_on_new_snapshot'] = {'n': len(allf), 'mape': round(med([abs(math.exp(-e) - 1) for e in allf_res]), 4),
                                 'median_resid_pct': round(math.exp(med(allf_res)) - 1, 4)}

    # ---------- 3. Гедоник үнийн индекс (бүх зар, хугацааны хувьсагчтай) ----------
    hed = {}
    for scope, fo in [('all', False), ('fresh', True)]:
        a = model_rows(base_filter(old_raw, fo)); b = model_rows(base_filter(new_raw, fo))
        for r in a: r['_new'] = False
        b = [dict(r, _new=True) for r in b]
        m = clean_and_cv(a + b, period=True, folds=2)
        coef = dict(zip([c[0] for c in m['cols']], m['beta']))
        hed[scope] = {f: round(math.exp(coef['new_' + f]) - 1, 4) for f in FAMS}
        for r in a: r.pop('_new', None)
    out['hedonic_period_effect'] = hed

    # ---------- 4. Нэгтгэсэн өгөгдлөөр дахин сургах ----------
    merged = {**old_u, **new_u}   # давхардсан зарын хамгийн сүүлийн үнэ
    merged = list(merged.values())
    tests = {}
    fresh_rows = model_rows(base_filter(merged, True))
    old_fresh = model_rows(base_filter(old_raw, True))
    tests['v5_repro_old_only'] = clean_and_cv(old_fresh)
    for lam in [0.5, 1, 2, 4]:
        tests[f'merged_lam{lam}'] = clean_and_cv(fresh_rows, lam=lam)
    tests['merged_inner'] = clean_and_cv(fresh_rows, inner=True)
    out['refit_tests'] = {k: {'n': len(v['clean']), 'mape': round(v['mape'], 4), 'within10': round(v['within10'], 3), 'by_fam': v['by_fam']}
                          for k, v in tests.items()}

    # Урагшлах тест: зөвхөн хуучин өгөгдлөөр сургаад шинээр гарсан зар дээр шалгах (v5 vs шинэ тохиргоо)
    fw = {}
    for lam in [0.5, 1, 2, 4]:
        m = tests['v5_repro_old_only'] if lam == 1 else clean_and_cv(old_fresh, lam=lam)
        coef = dict(zip([c[0] for c in m['cols']], m['beta']))
        errs = [abs(math.exp(pred_coef(r, coef)) / r['price'] - 1) for r in fwd]
        fw[f'lam{lam}'] = round(med(errs), 4) if errs else None
    out['forward_by_lambda'] = fw

    # λ-ийн ялгаа 10 удаагийн санамсаргүй CV-ийн хэлбэлзлээс бага байсан (robustness_check.py) тул v5-ийн λ=1-ийг хэвээр авна.
    best_key = 'merged_lam1'
    best = tests[best_key]
    res = [math.log(r['price']) - pred(r, best['cols'], best['beta']) for r in best['clean']]
    yc = {}
    for r in best['clean']: yc.setdefault(r['fam'], {}); yc[r['fam']][str(r['made'])] = yc[r['fam']].get(str(r['made']), 0) + 1
    model = {
        'version': 6, 'source': v5['source'], 'scraped': f'{OLD} + {NEW}', 'config': best_key,
        'n_listings': len(fresh_rows), 'n_fit': len(best['clean']),
        'cv_5fold': {'median_abs_pct_error': round(best['mape'], 4), 'within_10pct': round(best['within10'], 3), 'by_family': best['by_fam']},
        'residual_quantiles_log': {k: round(q(res, f), 3) for k, f in [('p10', .1), ('p25', .25), ('p75', .75), ('p90', .9)]},
        'formula': v5['formula'], 'scope': v5['scope'] + f' — {OLD} ба {NEW}-ний татлагыг нэгтгэсэн (давхардвал сүүлийн үнэ)',
        'coef': {c[0]: round(b, 4) for c, b in zip(best['cols'], best['beta'])},
        'year_counts': yc,
    }
    out['chosen'] = best_key
    with open(os.path.join(ROOT, 'models', f'model_{NEW}_v6_2026fresh.json'), 'w', encoding='utf-8') as f:
        json.dump(model, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, 'data', f'compare_{OLD}_{NEW}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
