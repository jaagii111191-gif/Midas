# Олон татлагыг харьцуулж, бүгдийг нэгтгэн загварыг дахин сургана (v7-оос).
# Хэрэглэх: python tools/compare_multi.py 2026-10-01 2026-10-04 2026-10-11
#  - Сүүлийн огноог өмнөх огноо бүртэй харьцуулна (ижил зарын үнэ, он/гүйлт тэнцүүлсэн индекс).
#  - Өмнөх хамгийн шинэ загварыг (models/) сүүлд шинээр гарсан зар дээр шалгана.
#  - Бүх огноог нэгтгэн λ-г давтан CV-ээр сонгож шинэ загвар хадгална.
import glob, json, math, os, random, statistics, sys
sys.path.insert(0, os.path.dirname(__file__))
import compare_and_refit as M

DATES = sys.argv[1:]
LAST = DATES[-1] if DATES else None
ROOT = M.ROOT
FAMS = M.FAMS
med = M.med


def pair_report(old_raw, new_raw):
    # Prius55 ангиллыг зөвхөн 10-11-нээс татсан тул огноо хоорондын харьцуулалтад оруулахгүй
    old_u = {r['u']: r for r in old_raw if r['price'] and r.get('slug') != 'Prius55'}
    new_u = {r['u']: r for r in new_raw if r['price'] and r.get('slug') != 'Prius55'}
    same = [(old_u[u], new_u[u]) for u in old_u.keys() & new_u.keys()]
    gone = [old_u[u] for u in old_u.keys() - new_u.keys()]
    added = [new_u[u] for u in new_u.keys() - old_u.keys()]
    rep = {'same': len(same), 'gone': len(gone), 'added': len(added), 'by_fam': {}}
    for f in FAMS + ['all']:
        sel = lambda r: f == 'all' or r['fam'] == f
        # ±50%-иас их үсрэлт = бичлэгийн алдаа засвар (жишээ 1.95 → 19.5), дунджид оруулахгүй
        ch = [c for a, b in same if sel(a) and abs(c := b['price'] / a['price'] - 1) < 0.5]
        moved = [c for c in ch if abs(c) > 1e-9]
        rep['by_fam'][f] = {
            'n': len(ch), 'up': sum(c > 1e-9 for c in ch), 'down': sum(c < -1e-9 for c in ch),
            'mean_change_all': round(statistics.mean(ch), 4) if ch else None,
            'median_change_moved': round(med(moved), 4) if moved else None,
            'median_price_old': med([r['price'] for r in old_u.values() if sel(r)]),
            'median_price_new': med([r['price'] for r in new_u.values() if sel(r)]),
            'gone': sum(sel(r) for r in gone), 'added': sum(sel(r) for r in added),
        }
    big = sorted(((b['price'] / a['price'] - 1, a, b) for a, b in same if a['price'] != b['price']), key=lambda t: t[0])
    rep['biggest_cuts'] = [{'u': a['u'], 'old': a['price'], 'new': b['price'], 'pct': round(c, 3)} for c, a, b in big[:8]]
    rep['biggest_raises'] = [{'u': a['u'], 'old': a['price'], 'new': b['price'], 'pct': round(c, 3)} for c, a, b in big[-8:][::-1]]
    # Он, гүйлт, комплектацыг тэнцүүлсэн үнийн өөрчлөлт (гедоник индекс)
    hed = {}
    for scope, fo in [('all', False), ('fresh', True)]:
        a = [dict(r, _new=False) for r in M.model_rows(M.base_filter(list(old_u.values()), fo))]
        b = [dict(r, _new=True) for r in M.model_rows(M.base_filter(list(new_u.values()), fo))]
        m = M.clean_and_cv(a + b, period=True, folds=2)
        coef = dict(zip([c[0] for c in m['cols']], m['beta']))
        hed[scope] = {f: round(math.exp(coef['new_' + f]) - 1, 4) for f in FAMS}
        hed[scope + '_n'] = {'old': len(a), 'new': len(b)}
    rep['hedonic'] = hed
    return rep, added


def rep_cv(rows, lam, reps=10, folds=5):
    cols = M.build_cols(rows); M.cache(rows, cols)
    beta = M.fit(rows, cols, lam)
    res = [math.log(r['price']) - M.pred(r, cols, beta) for r in rows]
    sd = math.sqrt(sum(e * e for e in res) / len(res))
    clean = [r for r, e in zip(rows, res) if abs(e) < 3 * sd]
    cols = M.build_cols(clean); M.cache(clean, cols)
    out, fam = [], {}
    for s in range(reps):
        idx = list(range(len(clean))); random.Random(s).shuffle(idx)
        errs = []
        for k in range(folds):
            te = set(idx[k::folds])
            bb = M.fit([r for i, r in enumerate(clean) if i not in te], cols, lam)
            for i in te:
                e = abs(math.exp(M.pred(clean[i], cols, bb)) / clean[i]['price'] - 1)
                errs.append(e); fam.setdefault(clean[i]['fam'], []).append(e)
        out.append(med(errs))
    beta = M.fit(clean, cols, lam)
    w10 = None
    return dict(mape=sum(out) / len(out), lo=min(out), hi=max(out), clean=clean, cols=cols, beta=beta,
                by_fam={f: round(med(v), 4) for f, v in fam.items()})


def main():
    raws = {d: M.load(d) for d in DATES}
    new_raw = raws[LAST]
    out = {'dates': DATES, 'counts': {d: sum(1 for r in v if r['price']) for d, v in raws.items()}, 'pairs': {}}

    # ---------- 1. Сүүлийн татлагыг өмнөх бүртэй харьцуулах ----------
    added_since_prev = None
    for d in DATES[:-1]:
        rep, added = pair_report(raws[d], new_raw)
        out['pairs'][f'{d}→{LAST}'] = rep
        if d == DATES[-2]: added_since_prev = added

    # ---------- 2. Өмнөх загварыг шинэ зар дээр шалгах ----------
    prev_path = sorted(glob.glob(os.path.join(ROOT, 'models', 'model_*_2026fresh.json')))[-1]
    prev = json.load(open(prev_path, encoding='utf-8'))
    fwd = M.model_rows(M.base_filter(added_since_prev, True))
    res = [math.log(r['price']) - M.pred_coef(r, prev['coef']) for r in fwd]
    out['prev_model_forward'] = {
        'model': os.path.basename(prev_path), 'n': len(res),
        'mape': round(med([abs(math.exp(-e) - 1) for e in res]), 4) if res else None,
        'within10': round(sum(abs(math.exp(-e) - 1) < .1 for e in res) / len(res), 3) if res else None,
        'median_resid_pct': round(math.exp(med(res)) - 1, 4) if res else None,
        'by_fam': {f: {'n': len(v), 'median_resid_pct': round(math.exp(med(v)) - 1, 4)}
                   for f in FAMS if (v := [e for r, e in zip(fwd, res) if r['fam'] == f])},
    }
    snap = M.model_rows(M.base_filter(new_raw, True))
    sres = [math.log(r['price']) - M.pred_coef(r, prev['coef']) for r in snap]
    out['prev_model_on_last_snapshot'] = {'n': len(sres), 'mape': round(med([abs(math.exp(-e) - 1) for e in sres]), 4),
                                         'median_resid_pct': round(math.exp(med(sres)) - 1, 4)}

    # ---------- 3. Бүгдийг нэгтгэж дахин сургах ----------
    merged = {}
    for d in DATES:
        for r in raws[d]:
            if r['price']: merged[r['u']] = r            # давхардвал хамгийн сүүлийн үнэ
    rows = M.model_rows(M.base_filter(list(merged.values()), True))
    tests = {lam: rep_cv(rows, lam) for lam in [0.5, 1, 2]}
    out['refit'] = {f'lam{l}': {'mape': round(t['mape'], 4), 'lo': round(t['lo'], 4), 'hi': round(t['hi'], 4), 'n': len(t['clean']), 'by_fam': t['by_fam']}
                    for l, t in tests.items()}
    lam = min(tests, key=lambda l: tests[l]['mape'])
    if abs(tests[lam]['mape'] - tests[1]['mape']) < (tests[1]['hi'] - tests[1]['lo']):
        lam = 1          # ялгаа CV-ийн хэлбэлзлээс бага бол өмнөхтэй ижил λ=1
    best = tests[lam]
    res = [math.log(r['price']) - M.pred(r, best['cols'], best['beta']) for r in best['clean']]
    errs_in = None
    m5 = M.clean_and_cv(rows, lam=lam)       # өмнөх хувилбаруудтай харьцуулах 5-fold (тогтмол хуваалт)
    yc = {}
    for r in best['clean']: yc.setdefault(r['fam'], {}); yc[r['fam']][str(r['made'])] = yc[r['fam']].get(str(r['made']), 0) + 1
    ver = prev.get('version', 6) + 1
    model = {
        'version': ver, 'source': prev['source'], 'scraped': ' + '.join(DATES), 'config': f'lam{lam}',
        'n_listings': len(rows), 'n_fit': len(best['clean']),
        'cv_5fold': {'median_abs_pct_error': round(m5['mape'], 4), 'within_10pct': round(m5['within10'], 3), 'by_family': m5['by_fam']},
        'cv_repeated': {'mean_mape': round(best['mape'], 4), 'range': [round(best['lo'], 4), round(best['hi'], 4)]},
        'residual_quantiles_log': {k: round(M.q(res, f), 3) for k, f in [('p10', .1), ('p25', .25), ('p75', .75), ('p90', .9)]},
        'formula': prev['formula'], 'scope': prev['scope'].split(' — ')[0] + ' — ' + ', '.join(DATES) + '-ний татлагыг нэгтгэсэн (давхардвал сүүлийн үнэ)',
        'coef': {c[0]: round(b, 4) for c, b in zip(best['cols'], best['beta'])},
        'year_counts': yc,
    }
    out['chosen'] = model['config']; out['new_model'] = f'model_{LAST}_v{ver}_2026fresh.json'
    with open(os.path.join(ROOT, 'models', out['new_model']), 'w', encoding='utf-8') as f:
        json.dump(model, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, 'data', f'compare_multi_{LAST}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'pairs'}, ensure_ascii=False, indent=1))
    for k, p in out['pairs'].items():
        print('==', k, 'same', p['same'], 'gone', p['gone'], 'added', p['added'])
        print('   all', p['by_fam']['all'])
        print('   hedonic', p['hedonic'])


if __name__ == '__main__':
    main()
