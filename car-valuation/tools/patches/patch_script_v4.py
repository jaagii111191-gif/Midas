p = r'E:\tttt\car-valuation\scrape_and_fit.js'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    if a not in s:
        print('MISSING:', a[:80])
    s = s.replace(a, b)

rep("// unegui.mn машины үнэлгээний загварыг шинэчлэх скрипт (v2).", "// unegui.mn машины үнэлгээний загварыг шинэчлэх скрипт (v4).")
rep("model_YYYY-MM-DD_v2.json", "model_YYYY-MM-DD_v4.json")
rep("km: g('Явсан'), cond: g('Нөхцөл'), drive: g('Хөтлөгч'), fuel: g('Хөдөлгүүр'), lease: g('Лизинг'),",
    "km: g('Явсан'), cond: g('Нөхцөл'), drive: g('Хөтлөгч'), fuel: g('Хөдөлгүүр'), lease: g('Лизинг'),\n      wheel: g('Хүрд'), inner: g('Дотор өнгө'), trans: g('Хурдны хайрцаг'), type: g('Төрөл'), doors: g('Хаалга'),")
rep("    const fresh = /аваагүй|00 гүйлт/.test(a.cond || '');",
    "    const fresh = /аваагүй|00 гүйлт/.test(a.cond || '');\n    const ck = /аваагүй/.test(a.cond || '') ? 'fresh' : /00/.test(a.cond || '') ? 'z00' : /Дугаартай нь/.test(a.cond || '') ? 'withplate' : 'reg';")
rep("      lease: !!a.lease && !/Лизинггүй/.test(a.lease),",
    "      lease: a.lease || '', ck, wheel: a.wheel || '', inner: a.inner || '',")
rep("      pearl: /Сувдан/.test(a.color || ''), white: a.color === 'Цагаан', black: a.color === 'Хар', gray: /саарал/i.test(a.color || ''),",
    "      colg: (c => /Сувдан/.test(c) ? 'pearl' : c === 'Цагаан' ? 'white' : c === 'Хар' ? 'black' : /саарал/i.test(c) ? 'gray' : c === 'Улаан' ? 'red' : /Хөх|Цэнхэр/i.test(c) ? 'blue' : /Хүрэн|Бор|Боронзон/.test(c) ? 'brown' : 'other')(a.color || ''),")
# grades relative to base grade; unknown as own dummy
rep("      GRADES[f].forEach(([g]) => add('g_' + f + '_' + g, 1.5, r => r.fam === f && r.grade === g ? 1 : 0));",
    "      GRADES[f].map(g => g[0]).concat(['']).filter(g => g !== BASEG[f]).forEach(g => add('g_' + f + '_' + (g || 'unk'), .3, r => r.fam === f && r.grade === g ? 1 : 0));\n      add('lhd_' + f, .5, r => r.fam === f && r.wheel === 'Зөв' ? 1 : 0);")
rep("    ['ub', 'roof', 'jbl', 'cam360', 'hud', 'leather', 'radar', 'pearl', 'white', 'black', 'gray', 'is40', 'is51', 'awd',\n     'winter', 'led', 'modellista', 'battery', 'dealer', 'urgent', 'nego', 'swap', 'lease'].forEach(b => add(b, 1, r => r[b] ? 1 : 0));",
    "    ['ub', 'roof', 'jbl', 'cam360', 'hud', 'leather', 'radar', 'is40', 'is51', 'awd',\n     'winter', 'led', 'modellista', 'battery', 'dealer', 'urgent', 'nego', 'swap'].forEach(b => add(b, 1, r => r[b] ? 1 : 0));\n    ['pearl', 'white', 'black', 'gray', 'red', 'blue', 'brown'].forEach(c => add('c_' + c, .3, r => r.colg === c ? 1 : 0));\n    ['ББСБ лизингтэй', 'Банкны лизингтэй', 'Хувь лизингтэй'].forEach(v => add('lease=' + v, .5, r => r.lease === v ? 1 : 0));\n    ['withplate', 'z00'].forEach(v => add('cond=' + v, .5, r => r.ck === v ? 1 : 0));\n    ['Саарал', 'Бусад', 'Шаргал', 'Цагаан шар', 'Бор'].forEach(v => add('inner=' + v, .5, r => r.inner === v ? 1 : 0));")
rep("  const gradeOf = (fam, s) =>", "  const BASEG = { alpha: 's', p50: 's', camry: 'g', harrier: 'premium' };   // комплектацын суурь\n  const gradeOf = (fam, s) =>")
rep("const fit = (rows, cols, lam = 1) => { const p = cols.length", "const fit = (rows, cols, lam = 1) => { const p = cols.length")
open(p, 'w', encoding='utf-8').write(s)
print('done')
