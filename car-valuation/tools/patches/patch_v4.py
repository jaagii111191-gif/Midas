import json, re, os
os.chdir(r'E:\tttt\car-valuation')
C = json.loads('''{"int_alpha":3.4513,"yr_alpha":0.0667,"km_alpha":0.0497,"y_alpha_2007":0.0709,"y_alpha_2011":-0.009,"y_alpha_2012":-0.0423,"y_alpha_2013":-0.0853,"y_alpha_2014":-0.0988,"y_alpha_2015":0.0287,"y_alpha_2016":0.0718,"y_alpha_2017":0.0461,"y_alpha_2018":0.019,"y_alpha_2019":0.0263,"y_alpha_2020":-0.0039,"y_alpha_2021":0.0073,"y_alpha_2022":-0.0307,"g_alpha_gs":0.1283,"g_alpha_gtour":0.0263,"g_alpha_stour":0.0361,"g_alpha_tune":0.0181,"g_alpha_lsel":0,"g_alpha_g":-0.0017,"g_alpha_l":-0.0113,"g_alpha_unk":-0.0099,"ymnf_alpha":-0.0701,"int_p50":3.2797,"yr_p50":0.0627,"km_p50":0.0393,"y_p50_2015":0.0153,"y_p50_2016":0.0045,"y_p50_2017":-0.0265,"y_p50_2018":-0.0069,"y_p50_2019":-0.0033,"y_p50_2021":0.0352,"y_p50_2022":-0.0184,"g_p50_apt":0.0922,"g_p50_aprem":0.0557,"g_p50_atour":0.0649,"g_p50_stour":0.0168,"g_p50_ssafe":0.0735,"g_p50_a":0.0755,"g_p50_e":0,"g_p50_unk":0.0305,"ymnf_p50":-0.0649,"int_camry":3.5223,"yr_camry":0.1092,"km_camry":0.0436,"y_camry_2005":-0.0638,"y_camry_2007":-0.0529,"y_camry_2008":0.0262,"y_camry_2009":-0.1065,"y_camry_2010":-0.0799,"y_camry_2011":0.1586,"y_camry_2012":0.1434,"y_camry_2013":0.054,"y_camry_2014":0.0352,"y_camry_2015":0.0241,"y_camry_2016":0.006,"y_camry_2017":0.0374,"y_camry_2018":-0.0067,"y_camry_2019":-0.0539,"y_camry_2020":-0.0732,"y_camry_2021":-0.0574,"y_camry_2023":-0.054,"y_camry_2024":0.0466,"y_camry_2025":0.0169,"g_camry_wsl":0.0461,"g_camry_ws":-0.0101,"g_camry_gl":0.0554,"g_camry_x":-0.1954,"g_camry_unk":0.0043,"ymnf_camry":-0.0795,"int_harrier":3.959,"yr_harrier":0.0677,"km_harrier":0.0399,"y_harrier_2003":-0.0353,"y_harrier_2004":-0.0653,"y_harrier_2005":0.0626,"y_harrier_2006":0.0407,"y_harrier_2007":0.0138,"y_harrier_2008":-0.0231,"y_harrier_2009":-0.0025,"y_harrier_2010":-0.0185,"y_harrier_2011":-0.0262,"y_harrier_2012":-0.0364,"y_harrier_2013":0.059,"y_harrier_2014":0.0415,"y_harrier_2015":0.0077,"y_harrier_2016":0.0227,"y_harrier_2017":0.0116,"y_harrier_2018":-0.0016,"y_harrier_2019":-0.0354,"y_harrier_2020":0.0228,"y_harrier_2021":0.0086,"y_harrier_2022":0.0267,"y_harrier_2023":-0.0423,"y_harrier_2024":-0.0309,"g_harrier_zl":0.065,"g_harrier_z":-0.018,"g_harrier_gl":0,"g_harrier_pmetal":0.0164,"g_harrier_progress":-0.0324,"g_harrier_padv":-0.0033,"g_harrier_elegance":-0.0366,"g_harrier_grand":0,"g_harrier_airs":0,"g_harrier_lpkg":0.0042,"g_harrier_g":0.0072,"g_harrier_s":-0.0259,"g_harrier_unk":-0.0022,"ymnf_harrier":-0.0778,"c_pearl":-0.0024,"c_white":-0.0151,"c_black":-0.0427,"c_gray":-0.0399,"c_red":-0.0687,"c_blue":-0.0186,"c_brown":-0.0325,"gas_camry":0.0146,"gas_harrier":-0.0086,"cc35_harrier":0.1223,"cc20_harrier":-0.0386,"ub":0.0007,"roof":0.0342,"jbl":0.0154,"cam360":-0.0009,"hud":-0.0205,"leather":0.0198,"radar":0.0156,"is40":0.0314,"is51":0.0782,"awd":0.0008,"winter":0.0129,"led":-0.0001,"modellista":0.0516,"battery":0.1243,"dealer":-0.0252,"urgent":-0.0375,"nego":-0.0233,"swap":-0.007,"hasScore":0.014,"score":0.0325,"ymn_1":0.027,"ymn_2":0.0336,"ymn_3":0.058,"ymn_4":0.0786,"ymn_6":0.0797,"plated0":-0.0259,"cc24_camry":-0.0156,"kmpy":-0.1635,"lowkm":0.0373,"lease=ББСБ лизингтэй":0.0068,"lease=Банкны лизингтэй":0.004,"lease=Хувь лизингтэй":-0.0566,"cond=withplate":0.0045,"cond=z00":-0.0662,"lhd_alpha":0.1043,"lhd_p50":0.0935,"lhd_camry":0.0934,"lhd_harrier":0.0355,"inner=Саарал":-0.0109,"inner=Бусад":0.0112,"inner=Шаргал":-0.0179,"inner=Цагаан шар":-0.0007,"inner=Бор":0.0247}''')
YC = json.loads('''{"alpha":{"2011":88,"2012":192,"2013":155,"2014":74,"2015":90,"2016":66,"2017":34,"2018":24,"2019":18,"2020":4},"p50":{"2015":5,"2016":73,"2017":41,"2018":11,"2019":9},"camry":{"2009":3,"2011":19,"2012":67,"2013":30,"2014":21,"2015":19,"2016":20,"2017":26,"2018":23,"2019":11,"2020":5,"2021":9},"harrier":{"2003":3,"2004":5,"2005":75,"2006":54,"2007":57,"2008":62,"2009":39,"2010":33,"2011":14,"2012":8,"2014":111,"2015":63,"2016":47,"2017":43,"2018":28,"2019":21,"2020":14,"2021":20,"2022":7,"2023":4}}''')

m = json.load(open('model_2026-10-01_v3.json', encoding='utf-8'))
m.update({"version": 4, "coef": C, "n_listings": 2037, "n_fit": 1862,
  "residual_quantiles_log": {"p10": -0.111, "p25": -0.059, "p75": 0.056, "p90": 0.115},
  "changes_v4": "unegui.mn-ийн 15 талбарыг бүгдийг татаж тус бүрийг тестэлсэн; нөхцөл (3 төрөл), хүрд, лизинг (4 төрөл), дотор өнгийг загварт нэмсэн",
  "filter_test_mape": {"base": 0.0615, "cond": 0.0615, "wheel": 0.0614, "trans": 0.0616, "type": 0.0616, "doors": 0.0618, "lease": 0.062, "inner": 0.0612, "location_rural": 0.0615, "district": 0.0612, "cc_category": 0.0614, "drive_category": 0.0624, "fuel_category": 0.0617, "color_full_17": 0.0624, "all_13": 0.0637, "chosen_cond_wheel_lease_inner": 0.0608}})
m['cv_5fold'].update({"median_abs_pct_error": 0.0608, "within_10pct": 0.718})
m['audit']['data_quality'].update({"prius_fuel_not_hybrid": 247, "prius_cc_not_1.8": 143, "prius_listings": 978})
json.dump(m, open('model_2026-10-01_v4.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

p = 'unelgee.html'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    if a not in s:
        print('MISSING:', a[:80])
    s = s.replace(a, b)

s = re.sub(r'const C=\{.*?\};\n', lambda _: 'const C=' + json.dumps(C, ensure_ascii=False, separators=(',', ':')) + ';\n', s, flags=re.S)
s = re.sub(r'const YC=\{.*?\}\};', lambda _: 'const YC=' + json.dumps(YC, separators=(',', ':')) + ';', s, flags=re.S)
rep('const RQ={p10:-0.113,p25:-0.058,p75:0.056,p90:0.115};', 'const RQ={p10:-0.111,p25:-0.059,p75:0.056,p90:0.115};')
rep('загвар v3</div>', 'загвар v4</div>')
rep('unegui.mn · 2,036 зар', 'unegui.mn · 2,037 зар')

# condition: 3 options as on unegui
rep('''          <input type="radio" name="cond" id="c_fresh" value="fresh" checked><label for="c_fresh">Гаалиас гарсан<small>дугаар аваагүй</small></label>
          <input type="radio" name="cond" id="c_plated" value="plated"><label for="c_plated">Дугаартай<small>Монголд унасан</small></label>''',
'''          <input type="radio" name="cond" id="c_fresh" value="fresh" checked><label for="c_fresh">Дугаар аваагүй<small>гаалиас гарсан</small></label>
          <input type="radio" name="cond" id="c_withplate" value="withplate"><label for="c_withplate">Дугаартай нь зарна<small>дугаараа дагуулна</small></label>
          <input type="radio" name="cond" id="c_reg" value="reg"><label for="c_reg">Дугаар авсан<small>бүртгэлтэй</small></label>''')

# new unegui filter row after options fieldset
rep('''      <fieldset>
        <legend>Опшн</legend>
        <div class="checks" id="opts"></div>
      </fieldset>
''', '''      <fieldset>
        <legend>Опшн</legend>
        <div class="checks" id="opts"></div>
      </fieldset>

      <div class="row3">
        <div><label class="lbl" for="wheel">Хүрд</label>
          <select id="wheel"><option value="r">Буруу (Япон)</option><option value="l">Зөв</option></select></div>
        <div><label class="lbl" for="lease">Лизинг</label>
          <select id="lease"><option value="">Лизинггүй</option><option value="ББСБ лизингтэй">ББСБ лизингтэй</option><option value="Банкны лизингтэй">Банкны лизингтэй</option><option value="Хувь лизингтэй">Хувь лизингтэй</option></select></div>
        <div><label class="lbl" for="inner">Дотор өнгө</label>
          <select id="inner"><option value="">Хар</option><option value="Саарал">Саарал</option><option value="Шаргал">Шаргал</option><option value="Цагаан шар">Цагаан шар</option><option value="Бор">Бор</option><option value="Бусад">Бусад</option></select></div>
      </div>
''')
rep('.row2{display:grid;grid-template-columns:1fr 1fr;gap:14px}',
    '.row2{display:grid;grid-template-columns:1fr 1fr;gap:14px}\n.row3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}\n@media (max-width:620px){.row3{grid-template-columns:1fr}}')

# compute
rep('''  const plated=document.querySelector("input[name=cond]:checked").value==="plated";
  $("platedRow").hidden=!plated;
  if(plated){''', '''  const cond=document.querySelector("input[name=cond]:checked").value;
  const plated=cond!=="fresh";
  $("platedRow").hidden=!plated;
  if($("wheel").value==="l")add("Зөв хүрд",C["lhd_"+f]);
  const ls=$("lease").value;if(ls)add(ls,C["lease="+ls]);
  const inn=$("inner").value;if(inn)add("Дотор өнгө: "+inn,C["inner="+inn]);
  if(plated){
    if(cond==="withplate")add("Дугаартай нь зарна",C["cond=withplate"]);''')
rep('window._summary=`${m.name} ${y}, ${Math.round(km/1000)} мянган км, ${plated?"дугаартай":"гаалиас гарсан"}',
    'window._summary=`${m.name} ${y}, ${Math.round(km/1000)} мянган км, ${cond==="fresh"?"дугаар аваагүй":cond==="withplate"?"дугаартай нь":"дугаар авсан"}')

# accuracy note
rep('Сургалтад ороогүй зар дээр шалгахад үнийн дундаж зөрүү <b>6.0%</b> гарсан (анхны хувилбар 6.7%). Таамгийн 72% нь 10%-иас бага зөрүүтэй.',
    'Сургалтад ороогүй зар дээр шалгахад үнийн дундаж зөрүү <b>6.1%</b> гарсан (анхны хувилбар 6.7%). Таамгийн 72% нь 10%-иас бага зөрүүтэй. Загвар unegui.mn-ийн 15 шүүлтүүрийн талбарыг бүгдийг нь тестэлсэн.')
rep('<li>Жилд 20 мянган км-ээс их явсан бол үнэ буурна.</li>',
    '<li>Жилд 20 мянган км-ээс их явсан бол үнэ буурна.</li>\n        <li><b>Зөв хүрдтэй</b> Camry +9.8% (31 зар), <b>хувь лизингтэй</b> −5.5%.</li>')

# data quality rows
rep('<tr><td>Орж ирсэн он үйлдвэрлэснээсээ өмнө</td>',
    '<tr><td>Prius-ийн хөдөлгүүрийг буруу бөглөсөн</td><td class="r">247</td><td>Prius 40/41/50/51 бүгд хайбрид боловч 978 зарын 25% нь "Бензин" гэж бөглөгдсөн. Шүүлтүүрээр "Хайбрид" сонгоход эдгээр зар харагдахгүй.</td></tr>\n        <tr><td>Prius-ийн мотор багтаамж буруу</td><td class="r">143</td><td>1.8 л байх ёстой ч 1.5, 2.0, "Цахилгаан" гэх мэтээр бөглөсөн.</td></tr>\n        <tr><td>Орж ирсэн он үйлдвэрлэснээсээ өмнө</td>')

# filter test table before the cheapest/priciest tables
rep('''    <div class="two">
      <div>
        <h3>Үнэлгээнээс хамгийн хямд</h3>''', '''    <h3>unegui.mn шүүлтүүр тус бүрийн тест</h3>
    <div class="tbl"><table>
      <thead><tr><th>Шүүлтүүр</th><th>Үнэд нөлөө</th><th class="r">Алдаа</th><th>Шийдвэр</th></tr></thead>
      <tbody>
        <tr><td>Он, гүйлт, нөхцөл (Монголд унасан жил), өнгө, комплектац, опшн</td><td>Суурь загвар</td><td class="r">6.15%</td><td>Орсон</td></tr>
        <tr><td>Хүрд</td><td>Зөв хүрд: Prius +10–11% (6 зар), Camry +9.8% (31), Harrier +3.6%</td><td class="r">6.14%</td><td>Орсон</td></tr>
        <tr><td>Дотор өнгө</td><td>Бор +2.5%, шаргал −1.8%, саарал −1.1% (хартай харьцуулж)</td><td class="r">6.12%</td><td>Орсон</td></tr>
        <tr><td>Лизинг</td><td>Хувь лизинг −5.5%, ББСБ, банк ≈ 0</td><td class="r">6.20%</td><td>Орсон</td></tr>
        <tr><td>Нөхцөл (дугаартай нь / авсан)</td><td>Дугаартай нь зарна +0.5%</td><td class="r">6.15%</td><td>Орсон</td></tr>
        <tr><td>Дүүрэг</td><td>Хан-Уул +0.8%, Чингэлтэй −0.7%</td><td class="r">6.12%</td><td>Ороогүй, нөлөөгүй</td></tr>
        <tr><td>Хурдны хайрцаг</td><td>Механик 10 зар л байна</td><td class="r">6.16%</td><td>Ороогүй, өгөгдөл цөөн</td></tr>
        <tr><td>Төрөл, хаалга</td><td>Загвараас шууд хамаардаг, ±1%</td><td class="r">6.16–6.18%</td><td>Ороогүй, давхардал</td></tr>
        <tr><td>Хөдөлгүүр, мотор багтаамж (талбар)</td><td>Prius-ийн 25% нь буруу бөглөгдсөн</td><td class="r">6.14–6.17%</td><td>Ороогүй, тайлбараас уншина</td></tr>
        <tr><td>Хөтлөгч (талбар)</td><td>Harrier FWD −2.8%</td><td class="r">6.24%</td><td>Ороогүй, нарийвчлал буурсан</td></tr>
        <tr><td>Гадна өнгө 17 ангиллаар</td><td>Ягаан, улаан −7%</td><td class="r">6.24%</td><td>7 ангиллаар үлдээсэн</td></tr>
        <tr><td>Бүх 13 шүүлтүүр нэг дор</td><td>Хэт тохируулга</td><td class="r">6.37%</td><td>Ороогүй</td></tr>
        <tr><td><b>Сонгосон хослол</b></td><td>Нөхцөл + хүрд + лизинг + дотор өнгө</td><td class="r"><b>6.08%</b></td><td><b>Ашиглаж байна</b></td></tr>
      </tbody>
    </table></div>

    <div class="two">
      <div>
        <h3>Үнэлгээнээс хамгийн хямд</h3>''')
open(p, 'w', encoding='utf-8').write(s)
print('done')
