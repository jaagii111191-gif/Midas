# unelgee.html-ийг v8 загвараар шинэчлэх: Camry 50/70 үе, Prius 55 нэмсэн (2026-10-01 + 10-04 + 10-11).
import json, math, os, re, shutil, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import compare_and_refit as M

ROOT = M.ROOT
os.chdir(ROOT)
DATES = ['2026-10-01', '2026-10-04', '2026-10-11']
m6 = json.load(open('models/model_2026-10-11_v8_2026fresh.json', encoding='utf-8'))
cmp = json.load(open('data/compare_multi_2026-10-11.json', encoding='utf-8'))
C = m6['coef']
RQ = m6['residual_quantiles_log']
YC = {f: dict(sorted(v.items())) for f, v in m6['year_counts'].items()}
raws = [M.load(d) for d in DATES]
new_raw = raws[-1]
mg = {}
for raw in raws:
    for r in raw:
        if r['price']: mg[r['u']] = r
merged = list(mg.values())
fit_rows = M.model_rows(M.base_filter(merged, True))
snap = M.model_rows(M.base_filter(new_raw, True))
fw = cmp['prev_model_forward']
p01 = cmp['pairs']['2026-10-01→2026-10-11']
p04 = cmp['pairs']['2026-10-04→2026-10-11']
pct = lambda c: (math.exp(c) - 1) * 100
sp = lambda c: ('+' if c > 0 else '−' if c < 0 else '') + f'{abs(pct(c)):.1f}%'

# ---------- Комплектацын зарын тоо ----------
gcount = {}
for r in fit_rows: gcount[(r['fam'], r['grade'])] = gcount.get((r['fam'], r['grade']), 0) + 1
s = open('unelgee.html', encoding='utf-8').read()
shutil.copy('unelgee.html', 'reports/unelgee_v7_backup.html')
gm = re.search(r'const GRADES=\{.*?\]\]\};', s, flags=re.S).group(0)
def fix_counts(block):
    out, fam = [], None
    for line in block.split('\n'):
        f = re.search(r'(alpha|p50|camry|harrier):\[', line)
        if f: fam = f.group(1)
        line = re.sub(r'\["(\w*)","([^"]+)",\d+\]', lambda t: f'["{t.group(1)}","{t.group(2)}",{gcount.get((fam, t.group(1)), 0)}]', line)
        out.append(line)
    return '\n'.join(out)
s = s.replace(gm, fix_counts(gm))

# ---------- Хамгийн хямд / үнэтэй жагсаалт (10-11-ний зарууд) ----------
NAME = {'prius-40': 'Prius 40', 'prius-41': 'Prius 41', '50': 'Prius 50', 'prius-51': 'Prius 51', 'Prius55': 'Prius 55', 'camry': 'Camry', 'harrier': 'Harrier'}
aud = []
for r in snap:
    e = math.exp(M.pred_coef(r, C))
    idpart = r['u'].split('/')[2]
    aid, slug = idpart.split('_', 1)
    aud.append(dict(row=[aid, slug, NAME[r['slug']], r['made'], round((r['km'] or 0) / 1000), r['price'], round(e, 1)], ratio=r['price'] / e))
aud.sort(key=lambda a: a['ratio'])
LISTS = {'under': [a['row'] for a in aud[:10]], 'over': [a['row'] for a in aud[::-1][:10]]}
b = dict(u20=sum(a['ratio'] < .8 for a in aud), u10=sum(.8 <= a['ratio'] < .9 for a in aud), fair=sum(.9 <= a['ratio'] <= 1.1 for a in aud),
         o10=sum(1.1 < a['ratio'] <= 1.25 for a in aud), o25=sum(a['ratio'] > 1.25 for a in aud))
N = len(aud)

# ---------- Комплектац, өнгөний жингийн тест (5-fold) ----------
clean = M.clean_and_cv(fit_rows)['clean']
cols = M.build_cols(clean); M.cache(clean, cols)
names = [c[0] for c in cols]
gi = [i for i, k in enumerate(names) if k.startswith('g_')]
ci = [i for i, k in enumerate(names) if k.startswith('c_')]
idx = sorted(range(len(clean)), key=lambda i: (i * 2654435761) % 997)
wt = {}
for W in [1, 1.5, 2, 3]:
    errs = []
    for k in range(5):
        te = {i for j, i in enumerate(idx) if j % 5 == k}
        bb = M.fit([r for i, r in enumerate(clean) if i not in te], cols)
        cb = bb[names.index('c_black')]
        for i in te:
            r = clean[i]; x = dict(r['_x'])
            p = sum(bb[j] * v for j, v in x.items() if j not in gi and j not in ci)
            p += W * sum(bb[j] * x.get(j, 0) for j in gi)
            col = sum(bb[j] * x.get(j, 0) for j in ci)
            p += cb + W * (col - cb)
            errs.append(abs(math.exp(p) / r['price'] - 1))
    wt[W] = M.med(errs)
print('weight test', wt)

# ---------- Кодын өгөгдөл солих ----------
s = re.sub(r'const C=\{.*?\};\n', lambda _: 'const C=' + json.dumps(C, ensure_ascii=False, separators=(',', ':')) + ';\n', s, flags=re.S)
s = re.sub(r'const YC=\{.*?\}\};', lambda _: 'const YC=' + json.dumps(YC, separators=(',', ':')) + ';', s, flags=re.S)
s = re.sub(r'const LISTS=\{.*?\]\]\};', lambda _: 'const LISTS=' + json.dumps(LISTS, ensure_ascii=False, separators=(',', ':')) + ';', s, flags=re.S)
s = re.sub(r'const RQ=\{[^}]*\};', f'const RQ={{p10:{RQ["p10"]},p25:{RQ["p25"]},p75:{RQ["p75"]},p90:{RQ["p90"]}}};', s)


def rep(a, b_):
    global s
    if a not in s: print('MISSING:', a[:90])
    s = s.replace(a, b_)


rep(re.search(r'<div class="eyebrow">.*?</div>', s).group(0),
    f'<div class="eyebrow">unegui.mn · 2026 онд орж ирсэн, дугаар аваагүй {len(fit_rows)} зар · 2026.10.01 + 10.04 + 10.11 · загвар v8</div>')
rep(re.search(r'<select id="wgt">.*?</select>', s).group(0),
    '<select id="wgt">' + ''.join(f'<option value="{W}">×{W}{", өгөгдлөөр тогтоосон" if W == 1 else ""} (алдаа {wt[W]*100:.1f}%)</option>' for W in [1, 1.5, 2, 3]) + '</select>')
cv = m6['cv_5fold']
bf = cv['by_family']
rep(re.search(r'<p>Зөвхөн 2026 онд орж ирсэн.*?</ul>', s, flags=re.S).group(0),
    f'<p>Зөвхөн 2026 онд орж ирсэн, дугаар аваагүй {m6["n_fit"]} зар дээр сургасан (10.01, 10.04, 10.11-ний татлагыг нэгтгэсэн). Сургалтад ороогүй зар дээр шалгахад үнийн дундаж зөрүү <b>{cv["median_abs_pct_error"]*100:.1f}%</b> гарсан. Таамгийн {cv["within_10pct"]*100:.0f}% нь 10%-иас бага зөрүүтэй. Өмнөх v6 загварыг 10.04-өөс хойш шинээр гарсан {fw["n"]} зар дээр шалгахад {fw["mape"]*100:.1f}% зөрүүтэй байсан. <a href="https://claude.ai/artifact/PSkwCjrVN2pc4wne2T4xiN" target="_blank" rel="noopener">Үнийн өөрчлөлтийн тайлан</a></p>\n'
    f'      <ul><li>Prius 50/51: {bf["p50"]*100:.1f}%</li><li>Prius α: {bf["alpha"]*100:.1f}%</li><li>Prius 55: 6.2% (23 зар)</li><li>Harrier: {bf["harrier"]*100:.1f}%</li><li>Camry: {bf["camry"]*100:.1f}% (v7: 8.1%, 2017 оны 50/70 үеийг ялгасны дараа)</li></ul>')
g = lambda k: C.get(k, 0)
cb = g('c_black')
rep(re.search(r'<li><b>Комплектац \(суурьтай харьцуулж\):</b>.*?</li>', s).group(0),
    f'<li><b>Комплектац (суурьтай харьцуулж):</b> Prius α G\'s {sp(g("g_alpha_gs"))}, S Touring {sp(g("g_alpha_stour"))}, G Touring {sp(g("g_alpha_gtour"))}; '
    f'Prius 50 A Touring {sp(g("g_p50_atour"))}, S Safety Plus {sp(g("g_p50_ssafe"))}, A Premium {sp(g("g_p50_aprem"))}, S Touring {sp(g("g_p50_stour"))}; '
    f'Harrier Z Leather {sp(g("g_harrier_zl"))}; Camry G Leather {sp(g("g_camry_gl"))}, X {sp(g("g_camry_x"))}.</li>')
rep(re.search(r'<li><b>Өнгө \(хартай харьцуулж\):</b>.*?</li>', s).group(0),
    '<li><b>Өнгө (хартай харьцуулж):</b> ' + ', '.join(f'{n} {sp(g("c_" + k) - cb)}' for k, n in
        [('pearl', 'сувдан цагаан'), ('white', 'цагаан'), ('blue', 'хөх'), ('gray', 'саарал'), ('red', 'улаан')]) + '.</li>')
rep(re.search(r'<li><b>Люк</b>.*?</li>', s).group(0),
    f'<li><b>Люк</b> {sp(g("roof"))}, <b>360° камер</b> {sp(g("cam360"))}, Modellista/GR {sp(g("modellista"))}.</li>')
rep(re.search(r'<li><b>Зөв хүрдтэй</b>.*?</li>', s).group(0),
    f'<li><b>Зөв хүрдтэй</b> Camry {sp(g("lhd_camry"))}, <b>хувь лизингтэй</b> {sp(g("lease=Хувь лизингтэй"))}, "яаралтай" гэсэн зар {sp(g("urgent"))}.</li>')
known = sum(1 for r in fit_rows if r['grade'])
rep(re.search(r'<li>Шинэ гарсан зарын \d+% нь комплектацаа бичсэн\.', s).group(0),
    f'<li>Шинэ гарсан зарын {known / len(fit_rows) * 100:.0f}% нь комплектацаа бичсэн.')
rep(re.search(r'<p class="sub">Үнийн хуваарилалт ба жагсаалт:.*?</p>', s).group(0),
    f'<p class="sub">Үнийн хуваарилалт ба жагсаалт: 2026.10.11-ний байдлаар 2026 онд орж ирсэн, дугаар аваагүй {N} зар. Мэдээллийн зөрчлийн хүснэгт: 2026.10.01-ний бүх 2,037 зар.</p>')
rep(re.search(r'<div class="dist".*?</div>\s*</div>', s, flags=re.S).group(0),
    f'<div class="dist" role="img" aria-label="Үнийн хуваарилалт: 20%-иас хямд {b["u20"]}, 10–20% хямд {b["u10"]}, зохистой {b["fair"]}, 10–25% үнэтэй {b["o10"]}, 25%-иас үнэтэй {b["o25"]}">\n'
    f'      <div class="d1" style="flex:{b["u20"]}"></div><div class="d2" style="flex:{b["u10"]}"></div><div class="d3" style="flex:{b["fair"]}"></div><div class="d4" style="flex:{b["o10"]}"></div><div class="d5" style="flex:{b["o25"]}"></div>\n    </div>')
rep(re.search(r'<div class="dlegend">.*?</div>', s, flags=re.S).group(0),
    f'<div class="dlegend">\n      <span><i class="d1"></i>20%-иас хямд · {b["u20"]}</span><span><i class="d2"></i>10–20% хямд · {b["u10"]}</span><span><i class="d3"></i>Зохистой ±10% · {b["fair"]} ({b["fair"]/N*100:.0f}%)</span><span><i class="d4"></i>10–25% үнэтэй · {b["o10"]}</span><span><i class="d5"></i>25%-иас үнэтэй · {b["o25"]}</span>\n    </div>')
rep(re.search(r'<p class="hint">Шинэ гарсан машинуудын үнэ нэг цэгт төвлөрсөн:.*?</p>', s).group(0),
    f'<p class="hint">Шинэ гарсан машинуудын үнэ нэг цэгт төвлөрсөн: {b["fair"]/N*100:.0f}% нь үнэлгээнээс ±10%-ийн дотор. 10.01-ээс 10.11-ний хооронд зарын үнэ өсөөгүй: ижил {p01["by_fam"]["all"]["n"]:,} зарын {p01["by_fam"]["all"]["down"]} нь үнээ буулгаж, {p01["by_fam"]["all"]["up"]} нь өсгөсөн, дундаж өөрчлөлт {p01["by_fam"]["all"]["mean_change_all"]*100:+.1f}%. Холбоос нь unegui.mn дээрх зарыг нээнэ. Зар устсан бол нээгдэхгүй.</p>')
# ---------- v8: Prius 55, Camry-ийн үе ----------
rep('{id:"p51",name:"Prius 51",sub:"4-р үе",fam:"p50",dflt:2016},',
    '{id:"p51",name:"Prius 51",sub:"4-р үе",fam:"p50",dflt:2016},\n {id:"p55",name:"Prius 55",sub:"4-р үе · E-Four 4WD",fam:"p50",dflt:2016},')
rep('<div><label class="lbl" for="grade">Комплектац</label><select id="grade"></select></div>\n      </div>',
    '<div><label class="lbl" for="grade">Комплектац</label><select id="grade"></select></div>\n      </div>\n\n'
    '      <div id="genWrap" hidden><label class="lbl" for="gen">Camry-ийн үе (2017 онд хоёулаа гарсан)</label>\n'
    '        <select id="gen"><option value="">Мэдэхгүй</option><option value="50">Camry 50 (XV50, 2017.06 хүртэл)</option><option value="70">Camry 70 (XV70, 2017.07-оос)</option></select>\n'
    '        <div class="hint">Зар, гэрчилгээнээс шалгана: AVV50 = 50, AXVH70 = 70. Мэдэхгүй бол 2026 онд орж ирсэн 2017 оны Camry-ийн дийлэнх нь 70 үеийнх байдаг.</div></div>')
rep('  $("lo_awd").hidden=!(f==="harrier"||f==="p50");',
    '  $("lo_awd").hidden=!(f==="harrier"||f==="p50")||m.id==="p55";\n  $("genWrap").hidden=!(f==="camry"&&+$("year").value===2017);')
rep('  if(m.id==="p51")add("Prius 51 (ZVW51)",C.is51);',
    '  if(m.id==="p51")add("Prius 51 (ZVW51)",C.is51);\n  if(m.id==="p55")add("Prius 55 (E-Four 4WD)",(C.is55||0)+(C.awd||0));\n'
    '  if(f==="camry"){const gv=$("gen").value;$("genWrap").hidden=y!==2017;\n'
    '    if(y>=2018||(y===2017&&gv==="70"))add("Camry 70 үе",C.cam70||0);\n'
    '    else if(y===2017&&!gv)add("2017, үе тодорхойгүй (70 гэж тооцов)",C.cam70||0);}')
s = s.replace('өсгөсөн, дундаж өөрчлөлт -', 'өсгөсөн, дундаж өөрчлөлт −')
open('unelgee.html', 'w', encoding='utf-8').write(s)
print('buckets', b, 'N', N, 'grade known', known, len(fit_rows))
print('under', LISTS['under'][:3]); print('over', LISTS['over'][:3])
