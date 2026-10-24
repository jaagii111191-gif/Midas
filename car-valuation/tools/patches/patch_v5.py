import json, re, os
os.chdir(r'E:\tttt\car-valuation')
C = json.loads('''{"int_alpha":3.4821,"yr_alpha":0.0773,"km_alpha":0.0153,"y_alpha_2011":0.0496,"y_alpha_2012":-0.023,"y_alpha_2013":-0.058,"y_alpha_2014":-0.0443,"y_alpha_2015":-0.0214,"y_alpha_2016":0.0855,"y_alpha_2017":0.0429,"y_alpha_2018":0.0228,"y_alpha_2019":-0.0103,"y_alpha_2020":-0.0329,"y_alpha_2021":-0.0109,"g_alpha_gs":0.1556,"g_alpha_gtour":0.0335,"g_alpha_stour":0.0478,"g_alpha_tune":0.0134,"g_alpha_lsel":0,"g_alpha_g":-0.0011,"g_alpha_l":0,"g_alpha_unk":0.0071,"lhd_alpha":0,"int_p50":3.3383,"yr_p50":0.0448,"km_p50":0.0759,"y_p50_2015":0.0051,"y_p50_2016":0.0044,"y_p50_2017":-0.0155,"y_p50_2018":-0.0024,"y_p50_2019":0.0085,"g_p50_apt":0,"g_p50_aprem":0.0656,"g_p50_atour":0.0945,"g_p50_stour":0.0505,"g_p50_ssafe":0.0812,"g_p50_a":0.0259,"g_p50_e":0,"g_p50_unk":0.0748,"lhd_p50":0,"int_camry":3.607,"yr_camry":0.0839,"km_camry":0.0596,"y_camry_2011":0.008,"y_camry_2012":0.0148,"y_camry_2013":-0.069,"y_camry_2014":0.0099,"y_camry_2015":0.0173,"y_camry_2016":0.0122,"y_camry_2017":0.0453,"y_camry_2018":0.0005,"y_camry_2019":0.0006,"y_camry_2020":-0.0525,"y_camry_2021":0.0063,"y_camry_2025":0.0066,"g_camry_wsl":0.0182,"g_camry_ws":0.1078,"g_camry_gl":0.116,"g_camry_x":-0.2083,"g_camry_unk":0.0381,"lhd_camry":0.152,"int_harrier":4.059,"yr_harrier":0.0544,"km_harrier":0.0005,"y_harrier_2005":0.0458,"y_harrier_2006":0.0168,"y_harrier_2007":-0.011,"y_harrier_2008":-0.0233,"y_harrier_2009":-0.0353,"y_harrier_2010":-0.0107,"y_harrier_2011":0.0126,"y_harrier_2014":-0.023,"y_harrier_2015":-0.045,"y_harrier_2016":0.043,"y_harrier_2017":0.019,"y_harrier_2018":-0.0021,"y_harrier_2019":-0.0331,"y_harrier_2020":0.0493,"y_harrier_2021":0.0138,"y_harrier_2022":0.0014,"y_harrier_2023":-0.003,"y_harrier_2024":-0.0153,"g_harrier_zl":0.1086,"g_harrier_z":-0.0179,"g_harrier_gl":0,"g_harrier_pmetal":-0.0049,"g_harrier_progress":-0.0274,"g_harrier_padv":0.0035,"g_harrier_elegance":-0.0387,"g_harrier_grand":0,"g_harrier_airs":0,"g_harrier_lpkg":0.05,"g_harrier_g":-0.0313,"g_harrier_s":-0.0385,"g_harrier_unk":-0.0105,"lhd_harrier":0,"c_pearl":-0.0134,"c_white":-0.0237,"c_black":-0.0735,"c_gray":-0.0503,"c_red":-0.0858,"c_blue":-0.0287,"c_brown":-0.0014,"gas_camry":-0.0846,"gas_harrier":0.0202,"cc35_harrier":-0.0207,"cc20_harrier":-0.1436,"cc24_camry":-0.02,"roof":0.0398,"jbl":-0.0174,"cam360":0.0301,"hud":-0.0164,"leather":-0.001,"radar":0.0172,"is40":0.0397,"is51":0.1,"awd":-0.0225,"winter":0.0074,"led":-0.0179,"modellista":0.0283,"battery":0,"dealer":-0.0188,"urgent":-0.0418,"nego":0.0018,"swap":0,"hasScore":0.0091,"score":0.0259,"kmpy":-0.1066,"lowkm":0,"lease=ББСБ лизингтэй":-0.013,"lease=Банкны лизингтэй":-0.0011,"lease=Хувь лизингтэй":-0.0587}''')
YC = {"alpha": {"2011": 17, "2012": 42, "2013": 34, "2014": 15, "2015": 22, "2016": 33, "2017": 16, "2018": 9, "2019": 9, "2020": 3},
      "p50": {"2015": 3, "2016": 24, "2017": 26, "2018": 7, "2019": 8},
      "camry": {"2011": 3, "2012": 9, "2013": 4, "2015": 3, "2016": 3, "2017": 14, "2018": 7, "2019": 5, "2020": 4, "2021": 6},
      "harrier": {"2005": 3, "2006": 5, "2008": 5, "2009": 3, "2014": 19, "2015": 13, "2016": 14, "2017": 22, "2018": 14, "2019": 9, "2020": 6, "2021": 14, "2022": 5}}
GR = '''const GRADES={alpha:[["s","S (суурь)",38],["","Тодорхойгүй",96],["l","L",0],["g","G",25],["stour","S Touring Selection",14],["gtour","G Touring Selection",10],["tune","S Tune Black",13],["gs","G's",5]],
 p50:[["s","S (суурь)",16],["","Тодорхойгүй",34],["ssafe","S Safety Plus",3],["stour","S Touring Selection",5],["a","A",3],["atour","A Touring Selection",6],["aprem","A Premium",1],["apt","A Premium Touring",0]],
 camry:[["g","G (суурь)",13],["","Тодорхойгүй",41],["x","X",2],["gl","G Leather Package",3],["ws","WS",1],["wsl","WS Leather Package",1]],
 harrier:[["premium","Premium (суурь)",31],["","Тодорхойгүй",69],["s","S",2],["g","G",6],["lpkg","L Package (30-р цуврал)",1],["elegance","Elegance",3],["padv","Premium Advanced",16],["progress","Progress",3],["pmetal","Progress Metal & Leather",1],["z","Z",3],["zl","Z Leather",4]]};'''
LISTS = {"under": [["10767993","toyota-prius-40-2014-2026","Prius 40",2014,129,22.5,27.9],["10699891","toyota-prius-51-2016-2026","Prius 51",2016,200,29,35.5],["10773782","toyota-harrier-2017-2026","Harrier",2017,300,42.7,52],["10644930","toyota-camry-2017-2026","Camry",2017,96,39,47.2],["10768226","toyota-prius-41-2014-2026","Prius 41",2014,180,23,27.4],["10782592","toyota-prius-51-2016-2026","Prius 51",2016,133,30,34.9],["10532318","toyota-prius-51-2017-2026","Prius 51",2016,200,27.9,32.4],["10776353","toyota-prius-41-2014-2026","Prius 41",2014,202,23.2,27],["10744701","toyota-prius-41-2015-2026","Prius 41",2015,201,27,31.3],["10696081","toyota-prius-41-2013-2026","Prius 41",2013,120,23,26.6]],
 "over": [["10760927","toyota-harrier-2014-2026","Harrier",2014,202,66.5,49.2],["10708703","toyota-prius-41-2012-2026","Prius 41",2012,130,35,26.1],["10749898","toyota-prius-50-2017-2026","Prius 50",2017,189,42,31.5],["10732010","toyota-prius-41-2016-2026","Prius 41",2016,122,52,39],["10695037","toyota-prius-41-2016-2026","Prius 41",2016,150,49.5,38.2],["10767228","toyota-prius-41-2016-2026","Prius 41",2016,120,47,36.8],["10780298","toyota-prius-41-2012-2026","Prius 41",2012,200,32.5,25.5],["10780266","toyota-prius-41-2012-2026","Prius 41",2012,200,32.5,25.7],["10749229","toyota-prius-51-2016-2026","Prius 51",2016,211,43.2,34.7],["10706748","toyota-prius-41-2011-2026","Prius 41",2011,200,31,25.2]]}

m = json.load(open('model_2026-10-01_v4.json', encoding='utf-8'))
m.update({"version": 5, "scope": "Зөвхөн 2026 онд орж ирсэн, дугаар аваагүй (Нөхцөл = Дугаар аваагүй, Орж ирсэн он = 2026) зарууд",
  "n_listings": 502, "n_fit": 469, "coef": C, "year_counts": YC,
  "residual_quantiles_log": {"p10": -0.079, "p25": -0.041, "p75": 0.039, "p90": 0.084},
  "cv_5fold": {"median_abs_pct_error": 0.0497, "within_10pct": 0.778, "by_family": {"alpha": 0.051, "p50": 0.042, "camry": 0.092, "harrier": 0.047}},
  "weight_test_mape": {"x1": 0.0497, "x1.5": 0.0572, "x2": 0.0611, "x3": 0.077},
  "subset_tests_mape": {"base": 0.0502, "lease": 0.0494, "wheel": 0.05, "inner": 0.051, "lease_wheel_inner": 0.0518, "chosen_lease_wheel": 0.0497},
  "audit_subset": {"checked": 496, "under_20pct": 0, "under_10_20pct": 26, "fair_10pct": 425, "over_10_25pct": 37, "over_25pct": 8}})
for k in ["filter_test_mape", "changes_v4", "changes_v3", "weight_test", "fixes"]:
    m.pop(k, None)
json.dump(m, open('model_2026-10-01_v5_2026fresh.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

p = 'unelgee.html'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    if a not in s:
        print('MISSING:', a[:90])
    s = s.replace(a, b)

s = re.sub(r'const C=\{.*?\};\n', lambda _: 'const C=' + json.dumps(C, ensure_ascii=False, separators=(',', ':')) + ';\n', s, flags=re.S)
s = re.sub(r'const YC=\{.*?\}\};', lambda _: 'const YC=' + json.dumps(YC, separators=(',', ':')) + ';', s, flags=re.S)
s = re.sub(r'const GRADES=\{.*?\]\]\};', lambda _: GR, s, flags=re.S)
s = re.sub(r'const LISTS=\{.*?\]\]\};', lambda _: 'const LISTS=' + json.dumps(LISTS, ensure_ascii=False, separators=(',', ':')) + ';', s, flags=re.S)
s = re.sub(r'const RQ=\{[^}]*\};', 'const RQ={p10:-0.079,p25:-0.041,p75:0.039,p90:0.084};', s)

rep('<div class="eyebrow">unegui.mn · 2,037 зар · 2026.10.01 · загвар v4</div>',
    '<div class="eyebrow">unegui.mn · 2026 онд орж ирсэн, дугаар аваагүй 502 зар · 2026.10.01 · загвар v5</div>')
rep('Prius 40/41, 50/51, Camry, Harrier-ийн зах зээлийн үнийг он, гүйлт, нөхцөл, комплектац, опшн, өнгөөр нь тооцно.',
    '2026 онд гаалиас гарсан, дугаар аваагүй Prius 40/41, 50/51, Camry, Harrier-ийн зах зээлийн үнийг он, гүйлт, комплектац, опшн, өнгөөр нь тооцно.')

# condition fixed
rep('''      <fieldset>
        <legend>Нөхцөл</legend>
        <div class="seg">
          <input type="radio" name="cond" id="c_fresh" value="fresh" checked><label for="c_fresh">Дугаар аваагүй<small>гаалиас гарсан</small></label>
          <input type="radio" name="cond" id="c_withplate" value="withplate"><label for="c_withplate">Дугаартай нь зарна<small>дугаараа дагуулна</small></label>
          <input type="radio" name="cond" id="c_reg" value="reg"><label for="c_reg">Дугаар авсан<small>бүртгэлтэй</small></label>
        </div>
      </fieldset>
      <div class="row2" id="platedRow" hidden>
        <div><label class="lbl" for="imp">Монголд орж ирсэн он</label><select id="imp"></select></div>
        <div class="checks" style="align-self:end"><label><input type="checkbox" id="ub">УБ дугаартай</label></div>
      </div>
''', '''      <div class="fixed"><span class="lbl">Нөхцөл</span><span>Дугаар аваагүй · 2026 онд орж ирсэн</span></div>
''')
rep('''.row3{display:grid;''', '''.fixed{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;padding:8px 12px;border:1px dashed var(--line);border-radius:6px;background:var(--sunk);font-size:.9rem}
.fixed .lbl{margin:0}
.row3{display:grid;''')
rep('''        <div><label class="lbl" for="inner">Дотор өнгө</label>
          <select id="inner"><option value="">Хар</option><option value="Саарал">Саарал</option><option value="Шаргал">Шаргал</option><option value="Цагаан шар">Цагаан шар</option><option value="Бор">Бор</option><option value="Бусад">Бусад</option></select></div>
      </div>''', '''      </div>''')
rep('.row3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}', '.row3{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}')
rep('''$("imp").innerHTML=Array.from({length:NOW-2009},(_,i)=>NOW-i).map(y=>`<option value="${y}">${y}${y===NOW?" (энэ жил)":""}</option>`).join("");
$("imp").value=String(NOW-2);
''', '')
rep('''  const cond=document.querySelector("input[name=cond]:checked").value;
  const plated=cond!=="fresh";
  $("platedRow").hidden=!plated;
''', '''  const cond="fresh";
''')
rep('''  const inn=$("inner").value;if(inn)add("Дотор өнгө: "+inn,C["inner="+inn]);
  if(plated){
    if(cond==="withplate")add("Дугаартай нь зарна",C["cond=withplate"]);
    const ymn=Math.max(0,NOW-Math.max(+$("imp").value,y));
    const k=ymn===0?"plated0":ymn===1?"ymn_1":ymn===2?"ymn_2":ymn===3?"ymn_3":ymn<=5?"ymn_4":"ymn_6";
    add(ymn===0?"Энэ жил дугаар авсан":`Монголд ${ymn} жил унасан`,C[k]+C["ymnf_"+f]*Math.min(ymn,8));
    if($("ub").checked)add("УБ дугаар",C.ub);
  }
''', '')
rep('["modellista","Modellista / GR / обвес"],["battery","Шинэ хайбрид батерей"],', '["modellista","Modellista / GR / обвес"],')
rep('<span>Суурь: ${m.name} ${y}, ${GNAME[BASEG[f]]} грейд, хар өнгө, гаалиас гарсан, 150 мянган км</span>',
    '<span>Суурь: ${m.name} ${y}, ${GNAME[BASEG[f]]} грейд, хар өнгө, 150 мянган км</span>')
rep('<option value="1">×1, өгөгдлөөр тогтоосон (алдаа 6.0%)</option><option value="1.5">×1.5 (алдаа 6.2%)</option><option value="2">×2 (алдаа 6.4%)</option><option value="3">×3 (алдаа 7.1%)</option>',
    '<option value="1">×1, өгөгдлөөр тогтоосон (алдаа 5.0%)</option><option value="1.5">×1.5 (алдаа 5.7%)</option><option value="2">×2 (алдаа 6.1%)</option><option value="3">×3 (алдаа 7.7%)</option>')

# notes
rep('''      <p>Сургалтад ороогүй зар дээр шалгахад үнийн дундаж зөрүү <b>6.1%</b> гарсан (анхны хувилбар 6.7%). Таамгийн 72% нь 10%-иас бага зөрүүтэй. Загвар unegui.mn-ийн 15 шүүлтүүрийн талбарыг бүгдийг нь тестэлсэн.</p>
      <ul><li>Prius 50/51: 5.1%</li><li>Prius α: 5.5%</li><li>Harrier: 6.6%</li><li>Camry: 6.8%</li></ul>''',
'''      <p>Зөвхөн 2026 онд орж ирсэн, дугаар аваагүй 469 зар дээр сургасан. Сургалтад ороогүй зар дээр шалгахад үнийн дундаж зөрүү <b>5.0%</b> гарсан. Таамгийн 78% нь 10%-иас бага зөрүүтэй. Бүх зар дээр сургасан өмнөх загварынх 6.1% байсан.</p>
      <ul><li>Prius 50/51: 4.2%</li><li>Harrier: 4.7%</li><li>Prius α: 5.1%</li><li>Camry: 9.2% (63 зар, хоёр үе холилдсон)</li></ul>''')
rep('''        <li><b>Он ба загварын үе.</b> Prius α 2014→2016 онд 30 гаруй хувь өснө.</li>
        <li><b>Монголд унасан хугацаа</b> (Prius α): 1 жил −3.5%, 3 жил −13.5%, 6 жил −28.5%.</li>
        <li><b>Комплектац (суурьтай харьцуулж):</b> Prius α G's +13.5%, S Touring +3.5%; Prius 50 A +8.5%, S Safety Plus +8.6%, A Premium Touring +9.7%; Harrier Z Leather +6.4%; Camry X −17%.</li>
        <li><b>Өнгө (хартай харьцуулж):</b> сувдан цагаан +3.9%, цагаан +2.7%, хөх +2.4%, улаан −1.8%.</li>
        <li><b>Шинэ батерей</b> +13%, <b>Modellista/GR</b> +4.7%, люк +3%, JBL +2%.</li>
        <li>Жилд 20 мянган км-ээс их явсан бол үнэ буурна.</li>
        <li><b>Зөв хүрдтэй</b> Camry +9.8% (31 зар), <b>хувь лизингтэй</b> −5.5%.</li>''',
'''        <li><b>Он ба загварын үе.</b> Prius α 2015→2016 онд 20 орчим хувь өснө.</li>
        <li><b>Комплектац (суурьтай харьцуулж):</b> Prius α G's +16.8%, S Touring +4.9%, G Touring +3.4%, G ≈ S; Prius 50 A Touring +9.9%, S Safety Plus +8.5%, A Premium +6.8%, S Touring +5.2%; Harrier Z Leather +11.5%; Camry G Leather +12.3%, X −18.8%.</li>
        <li><b>Өнгө (хартай харьцуулж):</b> сувдан цагаан +6.2%, цагаан +5.1%, хөх +4.6%, саарал +2.3%, улаан −1.2%.</li>
        <li><b>Люк</b> +4.1%, <b>360° камер</b> +3.1%, Modellista/GR +2.9%.</li>
        <li><b>Зөв хүрдтэй</b> Camry +16%, <b>хувь лизингтэй</b> −5.7%, "яаралтай" гэсэн зар −4.1%.</li>''')
rep('<li>Зарын 70% нь комплектацаа бичдэггүй. Цөөн зартай комплектацын (1–5 зар) нөлөөг болгоомжтой хүлээж ав.</li>',
    '<li>Шинэ гарсан зарын 51% нь комплектацаа бичсэн. Цөөн зартай комплектацын (0–5 зар) нөлөөг болгоомжтой хүлээж ав. L, A Premium Touring-д зар байхгүй тул нөлөөг 0 гэж тооцно.</li>\n        <li>Дугаар авсан, Монголд унасан машины үнийг энэ хувилбар тооцохгүй.</li>')

# audit
rep('<p class="sub">Prius 40/41/50/51, Camry, Harrier-ийн 2,036 зарыг загвартай тулгаж, мэдээллийн зөрчил хайсан. 2026.10.01-ний байдлаар.</p>',
    '<p class="sub">Үнийн хуваарилалт ба жагсаалт: 2026 онд орж ирсэн, дугаар аваагүй 496 зар. Мэдээллийн зөрчлийн хүснэгт: бүх 2,037 зар. 2026.10.01-ний байдлаар.</p>')
rep('''    <div class="dist" role="img" aria-label="Үнийн хуваарилалт: 20%-иас хямд 41, 10–20% хямд 192, зохистой 1450, 10–25% үнэтэй 224, 25%-иас үнэтэй 50">
      <div class="d1" style="flex:41"></div><div class="d2" style="flex:192"></div><div class="d3" style="flex:1450"></div><div class="d4" style="flex:224"></div><div class="d5" style="flex:50"></div>
    </div>
    <div class="dlegend">
      <span><i class="d1"></i>20%-иас хямд · 41</span><span><i class="d2"></i>10–20% хямд · 192</span><span><i class="d3"></i>Зохистой ±10% · 1,450 (74%)</span><span><i class="d4"></i>10–25% үнэтэй · 224</span><span><i class="d5"></i>25%-иас үнэтэй · 50</span>
    </div>''', '''    <div class="dist" role="img" aria-label="Үнийн хуваарилалт: 20%-иас хямд 0, 10–20% хямд 26, зохистой 425, 10–25% үнэтэй 37, 25%-иас үнэтэй 8">
      <div class="d2" style="flex:26"></div><div class="d3" style="flex:425"></div><div class="d4" style="flex:37"></div><div class="d5" style="flex:8"></div>
    </div>
    <div class="dlegend">
      <span><i class="d1"></i>20%-иас хямд · 0</span><span><i class="d2"></i>10–20% хямд · 26</span><span><i class="d3"></i>Зохистой ±10% · 425 (86%)</span><span><i class="d4"></i>10–25% үнэтэй · 37</span><span><i class="d5"></i>25%-иас үнэтэй · 8</span>
    </div>''')
rep('<p class="hint">Хэт хямд зар нь бодит хямдрал байж болох ч ихэнхдээ хуучин 30-р цуврал Harrier байдаг: мөргөлдсөн, дугааргүй, эсвэл яаралтай зарж буй машин. Хэт үнэтэй зар нь ихэвчлэн зарын алдаа (Prius 41 2012 оных 42 сая), эсвэл загварт өгөгдөл цөөн шинэ үе (Camry 2024) байна.',
    '<p class="hint">Шинэ гарсан машинуудын үнэ нэг цэгт төвлөрсөн: 86% нь үнэлгээнээс ±10%-ийн дотор, 20%-иас хямд зар нэг ч байхгүй. Хамгийн үнэтэй жагсаалтын Prius 41-үүд ихэнхдээ тайлбартаа комплектацаа бичээгүй, эсвэл ижил машиныг давхар оруулсан (10780298, 10780266) зарууд.')
rep('<h3>Үнэлгээнээс хамгийн хямд</h3>', '<h3>Хамгийн хямд (2026, дугаар аваагүй)</h3>')
rep('<h3>Үнэлгээнээс хамгийн үнэтэй</h3>', '<h3>Хамгийн үнэтэй (2026, дугаар аваагүй)</h3>')
rep('<span class="hint">${pl?"дугаартай":"гаалиас гарсан"}</span>', '<span class="hint">дугаар аваагүй</span>')
rep('rows.map(([id,slug,n,y,pl,km,p,e])=>', 'rows.map(([id,slug,n,y,km,p,e])=>')
open(p, 'w', encoding='utf-8').write(s)
print('done')
