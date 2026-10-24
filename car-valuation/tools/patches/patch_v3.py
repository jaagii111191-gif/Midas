import json, re, os
os.chdir(r'E:\tttt\car-valuation')
C = json.loads('''{"int_alpha":3.4372,"yr_alpha":0.0678,"km_alpha":0.0568,"y_alpha_2007":0.0774,"y_alpha_2011":-0.0118,"y_alpha_2012":-0.0434,"y_alpha_2013":-0.0881,"y_alpha_2014":-0.1023,"y_alpha_2015":0.0274,"y_alpha_2016":0.073,"y_alpha_2017":0.0452,"y_alpha_2018":0.0195,"y_alpha_2019":0.027,"y_alpha_2020":-0.0038,"y_alpha_2021":0.0071,"y_alpha_2022":-0.0272,"g_alpha_gs":0.1269,"g_alpha_gtour":0.0231,"g_alpha_stour":0.034,"g_alpha_tune":0.0211,"g_alpha_lsel":0,"g_alpha_g":-0.0053,"g_alpha_l":-0.0147,"g_alpha_unk":-0.0133,"ymnf_alpha":-0.0694,"int_p50":3.2478,"yr_p50":0.0722,"km_p50":0.0503,"y_p50_2015":0.0224,"y_p50_2016":0.0086,"y_p50_2017":-0.0324,"y_p50_2018":-0.0159,"y_p50_2019":-0.013,"y_p50_2021":0.056,"y_p50_2022":-0.0257,"g_p50_apt":0.093,"g_p50_aprem":0.0571,"g_p50_atour":0.0585,"g_p50_stour":0.0184,"g_p50_ssafe":0.0822,"g_p50_a":0.082,"g_p50_e":0,"g_p50_unk":0.0347,"ymnf_p50":-0.0648,"int_camry":3.5006,"yr_camry":0.1114,"km_camry":0.0471,"y_camry_2005":-0.0669,"y_camry_2007":-0.0582,"y_camry_2008":0.0175,"y_camry_2009":-0.1072,"y_camry_2010":-0.0634,"y_camry_2011":0.1704,"y_camry_2012":0.1384,"y_camry_2013":0.0492,"y_camry_2014":0.0356,"y_camry_2015":0.0326,"y_camry_2016":0.0091,"y_camry_2017":0.0406,"y_camry_2018":-0.0146,"y_camry_2019":-0.0612,"y_camry_2020":-0.0779,"y_camry_2021":-0.054,"y_camry_2023":-0.0641,"y_camry_2024":0.0604,"y_camry_2025":0.014,"g_camry_wsl":0.0586,"g_camry_ws":-0.0114,"g_camry_gl":0.0559,"g_camry_x":-0.1877,"g_camry_unk":0.0147,"ymnf_camry":-0.0777,"int_harrier":3.9461,"yr_harrier":0.0685,"km_harrier":0.0446,"y_harrier_2003":-0.0332,"y_harrier_2004":-0.0626,"y_harrier_2005":0.0623,"y_harrier_2006":0.0413,"y_harrier_2007":0.0079,"y_harrier_2008":-0.0231,"y_harrier_2009":-0.0028,"y_harrier_2010":-0.0189,"y_harrier_2011":-0.0252,"y_harrier_2012":-0.0379,"y_harrier_2013":0.0573,"y_harrier_2014":0.0424,"y_harrier_2015":0.0067,"y_harrier_2016":0.0214,"y_harrier_2017":0.0127,"y_harrier_2018":0.0031,"y_harrier_2019":-0.0356,"y_harrier_2020":0.0206,"y_harrier_2021":0.0124,"y_harrier_2022":0.0276,"y_harrier_2023":-0.046,"y_harrier_2024":-0.0305,"g_harrier_zl":0.0617,"g_harrier_z":-0.0461,"g_harrier_gl":0,"g_harrier_pmetal":0.0131,"g_harrier_progress":-0.0317,"g_harrier_padv":-0.0012,"g_harrier_elegance":-0.038,"g_harrier_grand":0,"g_harrier_airs":0,"g_harrier_lpkg":0.0076,"g_harrier_g":0.0062,"g_harrier_s":-0.0119,"g_harrier_unk":-0.0015,"ymnf_harrier":-0.0776,"c_pearl":0.0079,"c_white":-0.0038,"c_black":-0.0307,"c_gray":-0.0268,"c_red":-0.0491,"c_blue":-0.0073,"c_brown":-0.0202,"gas_camry":0.0237,"gas_harrier":-0.0122,"cc35_harrier":0.1188,"cc20_harrier":-0.0392,"ub":0.0012,"roof":0.0296,"jbl":0.0197,"cam360":-0.0019,"hud":-0.0243,"leather":0.0199,"radar":0.0146,"is40":0.0296,"is51":0.0732,"awd":0.0015,"winter":0.01,"led":0,"modellista":0.0458,"battery":0.1224,"dealer":-0.0274,"urgent":-0.0363,"nego":-0.0216,"swap":-0.0109,"lease":0.0054,"hasScore":0.011,"score":0.0269,"ymn_1":0.0327,"ymn_2":0.0385,"ymn_3":0.062,"ymn_4":0.0803,"ymn_6":0.0799,"plated0":-0.0194,"cc24_camry":-0.0116,"kmpy":-0.1772,"lowkm":0.0454}''')

m = json.load(open('model_2026-10-01_v2.json', encoding='utf-8'))
m['version'] = 3
m['coef'] = C
m['residual_quantiles_log'] = {"p10": -0.113, "p25": -0.058, "p75": 0.056, "p90": 0.115}
m['cv_5fold']['median_abs_pct_error'] = 0.0602
m['cv_5fold']['within_10pct'] = 0.716
m['changes_v3'] = "Комплектацыг суурь грейдтэй (alpha/p50: S, camry: G, harrier: Premium), өнгийг 7 ангиллаар хартай харьцуулж тооцсон; grade/color ridge торгууль 1.5/1 -> 0.3/0.3"
m['weight_test_mape'] = {"x0.5": 0.059, "x1": 0.0602, "x1.5": 0.062, "x2": 0.064, "x3": 0.0706}
json.dump(m, open('model_2026-10-01_v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

p = 'unelgee.html'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    if a not in s:
        print('MISSING:', a[:70])
    s = s.replace(a, b)

s = re.sub(r'const C=\{.*?\};\n', lambda _: 'const C=' + json.dumps(C, separators=(',', ':')) + ';\n', s, flags=re.S)
rep('const RQ={p10:-0.111,p25:-0.058,p75:0.055,p90:0.114};', 'const RQ={p10:-0.113,p25:-0.058,p75:0.056,p90:0.115};')
rep('alpha:[["","Тодорхойгүй",605],["s","S",51]', 'alpha:[["s","S (суурь)",51],["","Тодорхойгүй",605]')
rep('p50:[["","Тодорхойгүй",107],["s","S",17]', 'p50:[["s","S (суурь)",17],["","Тодорхойгүй",107]')
rep('camry:[["","Тодорхойгүй",257],["x","X",2],["g","G",17]', 'camry:[["g","G (суурь)",17],["","Тодорхойгүй",257],["x","X",2]')
rep('harrier:[["","Тодорхойгүй",662],["s","S",3],["g","G",12],["lpkg","L Package (30-р цуврал)",1],["elegance","Elegance",3],["premium","Premium",53]',
    'harrier:[["premium","Premium (суурь)",53],["","Тодорхойгүй",662],["s","S",3],["g","G",12],["lpkg","L Package (30-р цуврал)",1],["elegance","Elegance",3]')
rep('const GNAME={};Object.values(GRADES).forEach(l=>l.forEach(([v,n])=>{if(v)GNAME[v]=n}));',
    'const GNAME={};Object.values(GRADES).forEach(l=>l.forEach(([v,n])=>{if(v)GNAME[v]=n.replace(" (суурь)","")}));\nconst BASEG={alpha:"s",p50:"s",camry:"g",harrier:"premium"};')
rep('$("grade").innerHTML=GRADES[f].map(([v,n,c])=>`<option value="${v}">${n}${v?` · ${c} зар`:""}</option>`).join("");',
    '$("grade").innerHTML=GRADES[f].map(([v,n,c])=>`<option value="${v}">${n} · ${c} зар</option>`).join("");$("grade").value="";')
rep('<select id="color"><option value="pearl">Сувдан цагаан</option><option value="white">Цагаан</option><option value="black">Хар</option><option value="gray">Саарал / мөнгөлөг</option><option value="other">Бусад өнгө</option></select>',
    '<select id="color"><option value="black">Хар (суурь)</option><option value="pearl">Сувдан цагаан</option><option value="white">Цагаан</option><option value="gray">Саарал / хар саарал</option><option value="blue">Хөх / цэнхэр</option><option value="brown">Хүрэн / бор / боронзон</option><option value="red">Улаан</option><option value="other">Бусад өнгө</option></select>')
rep('const COLOR={pearl:"Сувдан цагаан",white:"Цагаан",black:"Хар",gray:"Саарал",other:"Бусад өнгө"};',
    'const COLOR={pearl:"Сувдан цагаан",white:"Цагаан",black:"Хар",gray:"Саарал",blue:"Хөх",brown:"Хүрэн",red:"Улаан",other:"Бусад өнгө"};')
rep('''<option>4.5</option><option>5</option></select></div>
      </div>''', '''<option>4.5</option><option>5</option></select></div>
      </div>
      <div>
        <label class="lbl" for="wgt">Комплектац, өнгөний жин</label>
        <select id="wgt"><option value="1">×1, өгөгдлөөр тогтоосон (алдаа 6.0%)</option><option value="1.5">×1.5 (алдаа 6.2%)</option><option value="2">×2 (алдаа 6.4%)</option><option value="3">×3 (алдаа 7.1%)</option></select>
        <div class="hint">Өөрийн туршлагаар комплектац, өнгө илүү нөлөөлдөг гэж үзвэл жинг өсгөнө. Зарын өгөгдөл дээр шалгахад жин өсөх тусам нарийвчлал буурсан.</div>
      </div>''')
rep('  const g=$("grade").value;if(g)add("Комплектац: "+GNAME[g],C[`g_${f}_${g}`]);',
    '  const W=+$("wgt").value;\n  const g=$("grade").value;if(g!==BASEG[f])add(g?"Комплектац: "+GNAME[g]:"Комплектац тодорхойгүй",W*(C[`g_${f}_${g||"unk"}`]||0));')
rep('  const col=$("color").value;if(col!=="other")add("Өнгө: "+COLOR[col],C[col]);',
    '  const col=$("color").value;if(col!=="black")add("Өнгө: "+COLOR[col],W*((C["c_"+col]||0)-C.c_black));')
rep('const base=C["int_"+f]+C["yr_"+f]*(y-2015)+(C[`y_${f}_${y}`]||0);',
    'const base=C["int_"+f]+C["yr_"+f]*(y-2015)+(C[`y_${f}_${y}`]||0)+C.c_black;')
rep('<span>Суурь: ${m.name} ${y}, гаалиас гарсан, 150 мянган км</span>',
    '<span>Суурь: ${m.name} ${y}, ${GNAME[BASEG[f]]} грейд, хар өнгө, гаалиас гарсан, 150 мянган км</span>')
# notes
rep('<li><b>Комплектац:</b> Prius α G\'s +13.5%, S Touring +4.4%, Harrier Z Leather +5%, Camry X −11%.</li>',
    '<li><b>Комплектац (суурьтай харьцуулж):</b> Prius α G\'s +13.5%, S Touring +3.5%; Prius 50 A +8.5%, S Safety Plus +8.6%, A Premium Touring +9.7%; Harrier Z Leather +6.4%; Camry X −17%.</li>\n        <li><b>Өнгө (хартай харьцуулж):</b> сувдан цагаан +3.9%, цагаан +2.7%, хөх +2.4%, улаан −1.8%.</li>')
rep('<b>Шинэ батерей</b> +13%, <b>Modellista/GR</b> +5.6%, люк +2.9%, JBL +2.4%.', '<b>Шинэ батерей</b> +13%, <b>Modellista/GR</b> +4.7%, люк +3%, JBL +2%.')
rep('Сургалтад ороогүй зар дээр шалгахад үнийн дундаж зөрүү <b>5.9%</b> гарсан (өмнөх хувилбар 6.7%). Таамгийн 72% нь 10%-иас, 87% нь 15%-иас бага зөрүүтэй.',
    'Сургалтад ороогүй зар дээр шалгахад үнийн дундаж зөрүү <b>6.0%</b> гарсан (анхны хувилбар 6.7%). Таамгийн 72% нь 10%-иас бага зөрүүтэй.')
rep('загвар v2</div>', 'загвар v3</div>')
open(p, 'w', encoding='utf-8').write(s)
print('done')
