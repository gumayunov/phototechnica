import json,re,html
T=open('template.html').read()
css=T[T.index('<style>')+7:T.index('</style>')]
cr=json.load(open('fs_credits.json'))
fix={'Ziko':'Ziko van Dijk','torstenbehrens':'Torsten Behrens','Torsten Behrens':'Torsten Behrens','tsuruta':'tsuruta yosuke','Trolle':'Kristoffer Trolle','Dambr':'Kārlis Dambrāns'}
def artist(a):
    for k,v in fix.items():
        if k in a: return v
    return a.strip()
def crs(f):
    c=cr[f]; return f'<span class="cr">Фото: <a href="{html.escape(c["page"])}" target="_blank" rel="noopener">{html.escape(artist(c["artist"]))}</a>, {html.escape(c["license"])}, Wikimedia Commons</span>'

# ---- B&W filter diagram
patches=[('небо',(90,150,225)),('облака',(238,238,242)),('листва',(70,140,60)),('красное',(205,45,55)),('кожа',(232,182,152))]
filters=[('Без фильтра',(0.30,0.59,0.11)),('+Ye жёлтый',(0.50,0.50,0.0)),('+R красный',(0.95,0.05,0.0)),('+G зелёный',(0.15,0.85,0.0))]
svg='<svg viewBox="0 0 820 290" role="img" aria-label="Как цветные фильтры меняют яркость цветов в чёрно-белом">'
x0=140; w=124; 
for i,(n,c) in enumerate(patches):
    x=x0+i*(w+8)
    svg+=f'<rect x="{x}" y="20" width="{w}" height="40" rx="6" fill="rgb{c}"/><text x="{x+w/2}" y="14" text-anchor="middle" font-size="12.5" fill="var(--muted)">{n}</text>'
svg+='<text x="0" y="45" font-size="13" font-weight="700" fill="var(--ink)">В цвете</text>'
for j,(fn,wts) in enumerate(filters):
    y=80+j*52
    svg+=f'<text x="0" y="{y+26}" font-size="13" font-weight="700" fill="var(--ink)">{fn}</text>'
    for i,(n,c) in enumerate(patches):
        g=int(round(min(255,c[0]*wts[0]+c[1]*wts[1]+c[2]*wts[2])))
        x=x0+i*(w+8)
        svg+=f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="6" fill="rgb({g},{g},{g})" stroke="var(--line)"/>'
svg+='</svg>'
bw_svg=svg

SIMS=[
 dict(k='provia',name='PROVIA / Стандарт',xs=True,film='Слайдовая плёнка Fujichrome Provia',manual='«Подходит для самых разных сюжетов»',c=3,s=3,good='всё подряд, когда не знаешь, что выбрать: путешествия, еда, предметы, яркий день',bad='—',tip='Нейтральная точка отсчёта. Сравнивай с ней остальные.'),
 dict(k='velvia',name='Velvia / Яркий',xs=True,film='Слайдовая плёнка Fujichrome Velvia, любимая плёнка пейзажистов',manual='«Яркая цветопередача, идеальна для пейзажей и природы»',c=5,s=5,good='пейзажи, закаты, цветы, осенний лес, море, яркие витрины',bad='портреты: кожа уходит в красноту; очень контрастный свет: тени проваливаются в черноту',tip='В пасмурный день оживляет серую картинку.'),
 dict(k='astia',name='ASTIA / Мягкий',xs=True,film='Слайдовая плёнка Fujichrome Astia для моды и портрета',manual='«Более мягкие цвета и контраст»',c=2,s=3,good='портреты, весна, цветы при мягком свете, детские фото, предметы',bad='когда нужен «удар» цвета и контраста',tip='Как Provia, только нежнее в тенях и на коже.'),
 dict(k='classic-chrome',name='CLASSIC CHROME',xs=True,film='Вдохновлена документальной журнальной фотографией на слайдах середины XX века',manual='«Мягкий цвет и усиленный контраст в тенях для спокойного вида»',c=4,s=2,good='улица, город, репортаж, пасмурные дни, архитектура, снег, старые машины',bad='праздники и сцены, где важен сочный цвет',tip='Самая популярная симуляция у уличных фотографов.'),
 dict(k='pro-neg-hi',name='PRO Neg. Hi',xs=True,film='Профессиональная негативная плёнка Fujicolor Pro',manual='«Для портретов, с чуть усиленным контрастом»',c=3,s=2,good='портреты на улице, люди в городе, свадьбы; пасмурный свет, которому не хватает контраста',bad='резкое полуденное солнце: может стать жёстко',tip='Кожа естественная, цвета спокойные.'),
 dict(k='pro-neg-std',name='PRO Neg. Std',xs=True,film='Та же профессиональная негативная плёнка, мягкий вариант',manual='«Для портретов с мягкими переходами и тонами кожи»',c=2,s=2,good='портреты при вспышке и в студии, съёмка в помещении; хорошо держит высокий ISO',bad='плоский серый свет: картинка станет вялой',tip='Самая «тихая» цветная симуляция: удобна для дальнейшей обработки.'),
 dict(k='classic-neg',name='CLASSIC Neg.',xs=True,film='Любительская негативная плёнка Fujicolor Superia, «фото из семейного альбома»',manual='«Насыщенный цвет и жёсткая тональность для глубины изображения»',c=5,s=4,good='улица, путешествия, лето, повседневность, ностальгия, закаты',bad='высокий ISO (3200 и выше): шум становится грубым; портреты, где важна точная кожа',tip='Сдвигает цвета: зелень уходит в бирюзу, небо в голубизну.'),
 dict(k='eterna',name='ETERNA / Кино',xs=True,film='Кинопленка Fujifilm Eterna',manual='«Мягкий цвет и глубокие тени, подходит для видео с плёночным видом»',c=1,s=1,good='видео, вечер, туман, спокойные сцены, контровой свет, высокий ISO',bad='когда нужна яркость и сочность',tip='Одна из лучших симуляций для съёмки в темноте.'),
 dict(k='eterna-bb',name='ETERNA BLEACH BYPASS',xs=True,film='Имитирует кинолабораторный приём bleach bypass («пропуск отбеливания»): холодная, жёсткая картинка, как в боевиках',manual='«Необычный цвет: низкая насыщенность и высокий контраст. Для фото и видео»',c=5,s=1,good='драматичный город, бетон, металл, заводы, хмурое небо',bad='портреты, нежные сюжеты, высокий ISO',tip='Сильный эффект: попробуй, но не делай его основным.'),
 dict(k='reala-ace',name='REALA ACE',xs=False,film='Негативная плёнка Fujicolor Reala',manual='На X-S10 нет. Нейтральные, точные цвета с чуть большим контрастом',c=3,s=3,good='—',bad='—',tip='Есть на X-S20 и более новых камерах, на X-S10 нет.'),
 dict(k='nostalgic-neg',name='NOSTALGIC Neg.',xs=False,film='Тёплый «янтарный» негатив в духе американской цветной фотографии 1970-х',manual='На X-S10 нет. Тёплые янтарные света, мягкий контраст',c=2,s=3,good='—',bad='—',tip='Есть на X-S20 и более новых камерах, на X-S10 нет.'),
 dict(k='acros',name='ACROS (+Ye, +R, +G)',xs=True,film='Чёрно-белая плёнка Neopan Acros 100',manual='«Ч/б с богатой детализацией и резкостью»',c=4,s=0,good='ч/б улица, архитектура, портреты с характером, фактуры',bad='ISO выше 3200: встроенное зерно становится грубым',tip='Добавляет своё «плёночное» зерно, которое зависит от ISO.'),
 dict(k='monochrome',name='MONOCHROME (+Ye, +R, +G)',xs=True,film='Простое цифровое ч/б',manual='«Съёмка в чёрно-белом»',c=3,s=0,good='ч/б при высоком ISO и в темноте, где Acros слишком зернит',bad='—',tip='Мягче и «чище», чем Acros.'),
 dict(k='sepia',name='SEPIA',xs=True,film='Коричневый тон старинных фотографий',manual='«Съёмка в тонах сепии»',c=3,s=0,good='ретро-стилизация, старые здания, открытки',bad='почти всё остальное: эффект быстро надоедает',tip='Сепию можно сделать и потом из любого снимка.'),
]
sims_json=json.dumps([{k:v for k,v in s.items()} for s in SIMS],ensure_ascii=False)

def bars(n,col):
    return ''.join(f'<i style="background:{col if i<n else "var(--line)"}"></i>' for i in range(5))
cards=''
for s in SIMS:
    if not s['xs']: continue
    img=f'img/mill-{s["k"]}.jpg'
    sat='<span class="muted">ч/б</span>' if s['s']==0 else f'<span class="bars">{bars(s["s"],"var(--t)")}</span>'
    cards+=f'''<article class="simcard" data-folio-id="card-{s["k"]}">
      <img src="{img}" alt="{s["name"]} — мельница" loading="lazy">
      <div class="simcard-b">
        <h3>{s["name"]}</h3>
        <p class="film">{s["film"]}</p>
        <p class="quote">{s["manual"]}</p>
        <div class="meters"><span>Контраст</span><span class="bars">{bars(s["c"],"var(--f)")}</span><span>Насыщенность</span>{sat}</div>
        <p><b>Хорошо:</b> {s["good"]}</p>
        {'<p><b>Не очень:</b> '+s["bad"]+'</p>' if s["bad"]!='—' else ''}
        <p class="tip">{s["tip"]}</p>
      </div>
    </article>'''

credit_items=[]; seen=set()
for f,c in sorted(cr.items()):
    if c['page'] in seen: continue
    seen.add(c['page'])
    credit_items.append(f'<li><a href="{html.escape(c["page"])}" target="_blank" rel="noopener">{html.escape(c["title"])}</a> — {html.escape(artist(c["artist"]))}, {html.escape(c["license"])}</li>')

MAIN='https://folio.fold-core.ru/a/bernhard/osnovy-fotografii-iso-f-vyderzhka-fokusn-fe0kh3se/'
page=f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Симуляции плёнки X-S10</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&family=Unbounded:wght@500;700&display=swap" rel="stylesheet">
<style>{css}
.backlink{{display:inline-flex;gap:8px;align-items:center;font-size:14px;font-weight:600;text-decoration:none;color:var(--muted);margin-top:28px}}
.backlink:hover{{color:var(--ink)}}
.viewer{{background:var(--paper);border:1px solid var(--line);border-radius:18px;padding:18px;margin:22px 0}}
.vstage{{position:relative;border-radius:12px;overflow:hidden;background:#111;aspect-ratio:3/2}}
.vstage img{{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;display:block}}
.vstage .b{{clip-path:inset(0 0 0 50%)}}
.vstage .split{{position:absolute;top:0;bottom:0;width:2px;background:#fff;left:50%;box-shadow:0 0 0 1px rgba(0,0,0,.3);pointer-events:none}}
.vstage .tagA,.vstage .tagB{{position:absolute;top:10px;padding:4px 10px;border-radius:999px;background:rgba(0,0,0,.6);color:#fff;font-size:13px;font-weight:600}}
.vstage .tagA{{left:10px}} .vstage .tagB{{right:10px}}
.simbtns{{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}}
.simbtns button{{border:1px solid var(--line);background:var(--paper);color:var(--ink);font:600 13px "Golos Text";padding:6px 11px;border-radius:999px;cursor:pointer}}
.simbtns button.on{{background:var(--ink);color:var(--bg);border-color:var(--ink)}}
.simbtns button.b-on{{box-shadow:0 0 0 2px var(--t)}}
.simbtns button.na{{opacity:.55}}
.simbtns button.na::after{{content:" ✕";font-weight:400}}
.vinfo{{margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.vinfo .box{{background:var(--soft);border-radius:10px;padding:12px 14px;font-size:14.5px}}
.vinfo .box b.h{{display:block;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}}
.cmp-row{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:12px;font-size:14px}}
.cmp-row input[type=range]{{flex:1;min-width:160px;accent-color:var(--t)}}
.simgrid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:20px 0}}
.simcard{{background:var(--paper);border:1px solid var(--line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column}}
.simcard img{{width:100%;aspect-ratio:3/2;object-fit:cover;display:block}}
.simcard-b{{padding:14px 16px 16px;font-size:14.5px}}
.simcard h3{{margin:0 0 4px;font-size:16px}}
.simcard p{{margin:0 0 8px}}
.simcard .film{{color:var(--muted);font-size:13.5px}}
.simcard .quote{{font-style:italic}}
.simcard .tip{{color:var(--muted);font-size:13.5px;margin:0}}
.meters{{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;align-items:center;font-size:12.5px;color:var(--muted);margin:6px 0 10px}}
.bars{{display:inline-flex;gap:3px}} .bars i{{width:18px;height:7px;border-radius:2px;display:inline-block}}
.muted{{color:var(--muted)}}
.recipe{{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start}}
.recipe table td:first-child{{color:var(--muted);white-space:nowrap}}
@media (min-width:1180px){{main{{margin-left:auto;margin-right:auto}}}}
@media (max-width:640px){{.simgrid,.vinfo,.recipe{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<main>
<a class="backlink" href="{MAIN}">← Основы фотографии</a>
<header class="hero" style="padding-top:20px" data-folio-id="intro">
  <div class="kicker">Fujifilm X-S10</div>
  <h1>Симуляции плёнки</h1>
  <p class="lead">Fujifilm почти сто лет делает фотоплёнку и встроила её «характер» в свои цифровые камеры. Симуляция плёнки — это готовый рецепт цвета и контраста, который камера применяет к снимку. Одна и та же сцена может выйти сочной, как открытка, спокойной, как журнальный репортаж, или чёрно-белой, как кадр 1950-х.</p>
  <nav class="chips" aria-label="Разделы">
    <a class="chip" href="#what">Что это</a><a class="chip" href="#compare">Сравнение</a><a class="chip" href="#all">Все 18 симуляций</a><a class="chip" href="#bw">Ч/б и фильтры</a><a class="chip" href="#when">Что для какой сцены</a><a class="chip" href="#recipe">Рецепты</a><a class="chip" href="#camera">Как включить</a>
  </nav>
</header>

<section id="what" data-folio-id="what">
  <span class="sec-num">01</span>
  <h2>Что делает симуляция</h2>
  <p>Матрица записывает «сырые» данные о свете. Чтобы получить картинку, камера решает, насколько насыщенными сделать цвета, в какую сторону сдвинуть оттенки (зелень теплее или холоднее, небо голубее или бирюзовее), насколько контрастными будут тени и света. Набор таких решений и есть симуляция. Fujifilm подбирала их так, чтобы они напоминали её настоящие плёнки: слайдовые Provia, Velvia и Astia, негативные Superia и Pro, кинопленку Eterna, чёрно-белую Acros.</p>
  <div class="note"><b>Что симуляция меняет, а что нет</b>
  <span style="display:block">• Меняет: цвет, насыщенность, контраст, у Acros ещё и зерно.</span>
  <span style="display:block">• Не меняет: экспозицию, фокус, резкость, шум. Тёмный снимок останется тёмным, нерезкий — нерезким. Это по-прежнему работа <a href="{MAIN}#triangle">диафрагмы, выдержки и ISO</a>.</span>
  <span style="display:block">• Видна сразу: X-S10 показывает выбранную симуляцию в видоискателе и на экране ещё до съёмки.</span>
  <span style="display:block">• Влияет на JPEG и видео. В RAW-файле хранятся «сырые» данные, и симуляцию можно сменить потом, прямо в камере.</span></div>
</section>

<section id="compare" data-folio-id="compare">
  <span class="sec-num">02</span>
  <h2>Одна сцена, разные плёнки</h2>
  <p>Фотограф Ziko van Dijk снял одни и те же сцены на Fujifilm X-S20, перебирая все симуляции подряд. X-S20 — преемник X-S10 с той же матрицей, поэтому общие симуляции выглядят так же. Две из них (Reala Ace и Nostalgic Neg., отмечены ✕) появились позже и на X-S10 их нет. Нажми на симуляцию, чтобы посмотреть её. Включи «Сравнить», чтобы поставить рядом две: шторку можно двигать.</p>
  <div class="viewer" data-folio-id="viewer">
    <div class="sim-top">
      <div class="seg" role="group" aria-label="Сцена" id="sceneSeg">
        <button type="button" data-s="mill" aria-pressed="true">Мельница</button>
        <button type="button" data-s="box" aria-pressed="false">Почтовый ящик</button>
        <button type="button" data-s="sheep" aria-pressed="false">Овцы под деревом</button>
      </div>
      <label style="font-size:14px;font-weight:600;display:flex;gap:8px;align-items:center"><input type="checkbox" id="cmpOn"> Сравнить две</label>
    </div>
    <div class="vstage" id="vstage"><img class="a" id="imgA" alt=""><img class="b" id="imgB" alt="" hidden><div class="split" id="split" hidden></div><span class="tagA" id="tagA"></span><span class="tagB" id="tagB" hidden></span></div>
    <div class="cmp-row" id="cmpRow" hidden><span>Шторка</span><input type="range" id="splitR" min="0" max="100" value="50" aria-label="Положение шторки"><span class="muted">Левая — <b id="lblA"></b>, правая — <b id="lblB"></b>. Обычный клик выбирает левую, клик с Shift или долгое нажатие — правую.</span></div>
    <div class="simbtns" id="simBtns"></div>
    <div class="vinfo"><div class="box"><b class="h">Описание Fujifilm</b><span id="vManual"></span><div class="muted" id="vFilm" style="font-size:13px;margin-top:6px"></div></div><div class="box"><b class="h">Подходит для</b><span id="vGood"></span><div class="muted" id="vTip" style="font-size:13px;margin-top:6px"></div></div></div>
    <figcaption id="vCredit" style="margin-top:10px"></figcaption>
  </div>
</section>

<section id="all" data-folio-id="all-sims">
  <span class="sec-num">03</span>
  <h2>Все 18 симуляций X-S10</h2>
  <p>В меню X-S10 их 18: девять цветных, восемь чёрно-белых (Acros и Monochrome, каждая без фильтра и с тремя цветными фильтрами) и сепия. Цитаты — описания из инструкции к X-S10 в переводе. Шкалы контраста и насыщенности — примерная оценка на глаз по описаниям Fujifilm и примерам.</p>
  <div class="simgrid">{cards}</div>
  <div class="note"><b>AUTO</b>В режимах AUTO и SP (сюжетные программы) X-S10 может выбрать симуляцию сам. Удобно, но учиться лучше, выбирая самой.</div>
</section>

<section id="bw" data-folio-id="bw">
  <span class="sec-num">04</span>
  <h2>Чёрно-белое и цветные фильтры</h2>
  <p>В чёрно-белой фотографии нет цвета, но разные цвета превращаются в разные оттенки серого. Фотографы на плёнку надевали на объектив цветные стёкла-фильтры: фильтр пропускает свет своего цвета и задерживает противоположный. У Acros и Monochrome в X-S10 есть такие фильтры, только встроенные.</p>
  <figure class="diagram" data-folio-id="bw-filters">{bw_svg}
    <figcaption>Схема: как один и тот же набор цветов выглядит в ч/б без фильтра и с фильтрами. Жёлтый и особенно красный фильтры затемняют синее небо, и белые облака на нём выделяются ярче. Красный ещё и высветляет красное. Зелёный высветляет листву и затемняет красное. Схема упрощённая: настоящий эффект зависит от оттенков в кадре.</figcaption>
  </figure>
  <div class="tbl-wrap" data-folio-id="bw-table"><table>
    <thead><tr><th>Фильтр</th><th>Описание Fujifilm</th><th>Когда пробовать</th></tr></thead>
    <tbody>
      <tr><td><b>Без фильтра</b></td><td>—</td><td>универсально, улица, интерьер</td></tr>
      <tr><td><b>+Ye</b> жёлтый</td><td>«Чуть усиливает контраст и затемняет небо»</td><td>пейзаж и город с небом, лёгкая драма</td></tr>
      <tr><td><b>+R</b> красный</td><td>«Усиливает контраст и сильно затемняет небо»</td><td>облака, горы, архитектура на фоне неба, сильная драма</td></tr>
      <tr><td><b>+G</b> зелёный</td><td>«Приятные тона кожи на портрете»</td><td>портреты, природа с листвой</td></tr>
    </tbody></table></div>
  <div class="pair" style="margin-top:20px" data-folio-id="bw-examples">
    <figure><img src="img/mill-acros.jpg" alt="Мельница в Acros" loading="lazy"><div class="lbl">ACROS</div></figure>
    <figure><img src="img/mill-monochrome.jpg" alt="Мельница в Monochrome" loading="lazy"><div class="lbl">MONOCHROME</div></figure>
  </div>
  <figcaption style="margin-top:6px">Acros контрастнее и глубже в тенях, Monochrome мягче.{crs("mill-acros.jpg")}</figcaption>
</section>

<section id="when" data-folio-id="when">
  <span class="sec-num">05</span>
  <h2>Какую симуляцию для какой сцены</h2>
  <p>Правильного ответа нет: это вопрос вкуса, и многие фотографы годами снимают на одну любимую симуляцию. Но для начала есть проверенные сочетания.</p>
  <div class="tbl-wrap" data-folio-id="cheatsheet"><table>
    <thead><tr><th>Сцена</th><th>Попробуй</th><th>Почему</th></tr></thead>
    <tbody>
      <tr><td>Солнечный пейзаж, море, горы</td><td><b>Velvia</b>, Provia</td><td>сочная зелень и синее небо</td></tr>
      <tr><td>Закат, золотой час</td><td><b>Classic Neg.</b>, Velvia, Pro Neg. Hi</td><td>тёплые тона и глубина</td></tr>
      <tr><td>Пасмурно, туман, дождь</td><td><b>Classic Chrome</b>, Eterna, Velvia</td><td>Chrome и Eterna подчеркнут настроение, Velvia добавит красок серому дню</td></tr>
      <tr><td>Портрет друга, мамы, бабушки</td><td><b>Astia</b>, Pro Neg. Std, Pro Neg. Hi</td><td>мягкая естественная кожа</td></tr>
      <tr><td>Улица, город, путешествие</td><td><b>Classic Chrome</b>, Classic Neg., Acros</td><td>«журнальный» или «плёночный» вид</td></tr>
      <tr><td>Цветы, осень, яркие предметы</td><td><b>Velvia</b>, Astia</td><td>Velvia — максимум цвета, Astia — нежнее</td></tr>
      <tr><td>Еда, вещи, учебный проект</td><td><b>Provia</b>, Astia</td><td>точные цвета без сюрпризов</td></tr>
      <tr><td>Вечер, помещение, высокий ISO</td><td><b>Eterna</b>, Pro Neg. Std, Monochrome</td><td>лучше переносят шум; Acros, Classic Neg. и Bleach Bypass на ISO 3200+ лучше не брать</td></tr>
      <tr><td>Драма: бетон, металл, гроза</td><td><b>Eterna Bleach Bypass</b>, Acros+R</td><td>жёсткий контраст, мало цвета</td></tr>
      <tr><td>Ч/б портрет</td><td><b>Acros+G</b></td><td>гладкая кожа</td></tr>
      <tr><td>Ч/б небо с облаками</td><td><b>Acros+R</b></td><td>тёмное небо, яркие облака</td></tr>
      <tr><td>Видео</td><td><b>Eterna</b></td><td>мягкий «киношный» вид, удобно обрабатывать</td></tr>
    </tbody></table></div>
  <p style="font-size:14px;color:var(--muted);margin-top:8px">По материалам инструкции Fujifilm, гайдов Digital Photography School и Fuji X Weekly и теста Fuji Rumors по съёмке в темноте (ссылки внизу).</p>

  <h3>Как это выглядит в жизни</h3>
  <div class="pair" data-folio-id="live-1">
    <figure><img src="img/live-porsche.jpg" alt="Серый Porsche 964 в Копенгагене, Classic Chrome" loading="lazy"><div class="lbl">Classic Chrome <small>· спокойный город в туманный день</small></div><figcaption>{crs("live-porsche.jpg")}</figcaption></figure>
    <figure><img src="img/live-train.jpg" alt="Поезд на заснеженных путях, Classic Chrome без обработки" loading="lazy"><div class="lbl">Classic Chrome <small>· зима, снимок без обработки</small></div><figcaption>{crs("live-train.jpg")}</figcaption></figure>
  </div>
  <div class="pair" style="margin-top:14px" data-folio-id="live-2">
    <figure><img src="img/live-castle.jpg" alt="Замок Мацумото, Classic Negative с зерном" loading="lazy"><div class="lbl">Classic Neg. + зерно <small>· путешествие, глубокое синее небо</small></div><figcaption>Снято на X-Pro3, у неё такая же матрица X-Trans 4, как у X-S10.{crs("live-castle.jpg")}</figcaption></figure>
    <figure><img src="img/live-teapot.jpg" alt="Красный чайник на пляже, Classic Negative" loading="lazy"><div class="lbl">Classic Neg. <small>· находка на пляже, X-S10</small></div><figcaption>{crs("live-teapot.jpg")}</figcaption></figure>
  </div>
</section>

<section id="recipe" data-folio-id="recipe">
  <span class="sec-num">06</span>
  <h2>Рецепты: симуляция плюс настройки</h2>
  <p>Симуляция — только основа. В меню качества изображения X-S10 есть ещё ручки, которыми её можно подкрутить. Набор «симуляция + настройки» фотографы называют <b>рецептом</b> и выкладывают в интернет, чтобы любой мог повторить «плёнку». Больше всего рецептов для X-Trans 4 (в том числе X-S10) собрано на сайте Fuji X Weekly.</p>
  <div class="tbl-wrap" data-folio-id="settings"><table>
    <thead><tr><th>Настройка</th><th>Варианты на X-S10</th><th>Что делает</th></tr></thead>
    <tbody>
      <tr><td><b>Grain Effect</b></td><td>Strong / Weak / Off; Large / Small</td><td>добавляет плёночное зерно</td></tr>
      <tr><td><b>Color Chrome Effect</b></td><td>Strong / Weak / Off</td><td>больше оттенков в очень насыщенных красных, жёлтых и зелёных (цветы, листва)</td></tr>
      <tr><td><b>Color Chrome FX Blue</b></td><td>Strong / Weak / Off</td><td>то же для синих: глубже небо и море</td></tr>
      <tr><td><b>White Balance</b> + сдвиг</td><td>Auto, Daylight, Kelvin…; сдвиг по красному и синему</td><td>делает картинку теплее или холоднее, «окрашивает» её</td></tr>
      <tr><td><b>Dynamic Range</b></td><td>DR100 / DR200 / DR400 / Auto</td><td>бережёт света от выгорания (<a href="{MAIN}#dr">динамический диапазон</a>); DR200 доступен от ISO 320, DR400 — от ISO 640</td></tr>
      <tr><td><b>Tone Curve</b></td><td>Highlights / Shadows: −2…+4</td><td>светлее или темнее света и тени, то есть контраст</td></tr>
      <tr><td><b>Color</b></td><td>−4…+4</td><td>насыщенность</td></tr>
      <tr><td><b>Sharpness</b>, <b>High ISO NR</b></td><td>−4…+4</td><td>резкость и шумоподавление; плёночные рецепты часто ставят NR −4, чтобы шум выглядел как зерно</td></tr>
      <tr><td><b>Clarity</b></td><td>−5…+5</td><td>локальный контраст; при значении не 0 камера дольше сохраняет снимок</td></tr>
    </tbody></table></div>

  <h3>Пример: рецепт «Back in the Day» на X-S10</h3>
  <div class="recipe" data-folio-id="recipe-example">
    <figure style="margin:0"><img src="img/live-beach.jpg" alt="Две женщины на деревянной скамейке на пляже в Травемюнде" loading="lazy"><figcaption>Fujifilm X-S10, 18–300 мм, f/5.6, 1/500, ISO 1000.{crs("live-beach.jpg")}</figcaption></figure>
    <div class="tbl-wrap"><table>
      <tbody>
        <tr><td>Симуляция</td><td><b>Classic Neg.</b></td></tr>
        <tr><td>Grain Effect</td><td>Off</td></tr>
        <tr><td>Color Chrome Effect</td><td>Off</td></tr>
        <tr><td>Color Chrome FX Blue</td><td>Weak</td></tr>
        <tr><td>White Balance</td><td>5600K, сдвиг +4 красный, −5 синий</td></tr>
        <tr><td>Dynamic Range</td><td>DR200</td></tr>
        <tr><td>Highlights / Shadows</td><td>+1.5 / −1.5</td></tr>
        <tr><td>Color</td><td>+2</td></tr>
        <tr><td>Sharpness / NR</td><td>−2 / −4</td></tr>
        <tr><td>Clarity</td><td>0</td></tr>
      </tbody></table></div>
  </div>
  <p style="font-size:14.5px;margin-top:12px">Настройки взяты из подписи автора к этому снимку. Сдвиг баланса белого в красный и от синего даёт тёплый «летний» тон, тени темнее, света ярче, как на старых отпечатках.</p>
  <div class="pair" style="margin-top:16px" data-folio-id="recipe-example-2">
    <figure><img src="img/live-wolf.jpg" alt="Дремлющий волк на траве" loading="lazy"><div class="lbl">Рецепт «Classic Analog» на основе PROVIA <small>· X-S10</small></div><figcaption>DR400, Highlight −2, Shadow −1, Color −2, NR −2, Daylight +1 красный −6 синий. Мягкий, слегка выцветший вид.{crs("live-wolf.jpg")}</figcaption></figure>
    <div class="note" style="margin:0"><b>Как пользоваться рецептами</b>Найди рецепт (например, на Fuji X Weekly или в их бесплатном приложении), выставь настройки и сохрани их в слот C1–C4 на диске режимов. Тогда «плёнку» можно будет включить одним поворотом. Рецепты для X-T3 и X-T30 тоже подходят X-S10. Отличаются только настройки зерна: у X-S10 есть ещё размер зерна.</div>
  </div>
</section>

<section id="camera" data-folio-id="camera">
  <span class="sec-num">07</span>
  <h2>Как включить на X-S10</h2>
  <ol class="tasks">
    <li><b>Левое колесо сверху</b> (без надписей) по умолчанию переключает симуляции. Крути и сразу смотри на результат в видоискателе. В меню колесу можно назначить и другую функцию.</li>
    <li><b>Кнопка Q</b>: быстрое меню, в нём есть Film Simulation, Grain, Dynamic Range и прочие пункты рецепта.</li>
    <li><b>Меню → I.Q. (качество изображения) → FILM SIMULATION</b> — полный список, там же выбираются фильтры для Acros и Monochrome.</li>
    <li><b>Свои рецепты</b>: меню I.Q. → EDIT/SAVE CUSTOM SETTING, сохрани в C1–C4, потом выбирай на диске режимов.</li>
    <li><b>Снимай в RAW + JPEG</b>: если симуляция не понравилась, в меню просмотра есть RAW CONVERSION. Камера пересоберёт JPEG из RAW с другой симуляцией. То же можно сделать на компьютере в бесплатной программе FUJIFILM X RAW Studio.</li>
    <li><b>Брекетинг симуляций</b>: в режимах серийной съёмки (BKT) есть Film Simulation Bracketing. Один снимок сохраняется сразу в трёх выбранных симуляциях. Удобно для сравнения.</li>
  </ol>
  <h3>Задания</h3>
  <ol class="tasks" data-folio-id="tasks">
    <li><b>Три плёнки, одна сцена.</b> Включи брекетинг симуляций с Velvia, Classic Chrome и Acros и сними что-нибудь яркое: витрину, клумбу, рынок. Какой снимок нравится больше и почему?</li>
    <li><b>Небо в ч/б.</b> В день с облаками сними одно и то же небо в Acros, Acros+Ye и Acros+R. Сравни, как темнеет небо.</li>
    <li><b>Портрет.</b> Сними подругу или кого-то из семьи в Astia, Pro Neg. Std и Classic Chrome. Где кожа выглядит лучше всего?</li>
    <li><b>Неделя одной плёнки.</b> Выбери одну симуляцию и неделю снимай только ей. Это лучший способ понять её характер.</li>
  </ol>
</section>

<section data-folio-id="sources">
  <h2 style="font-size:20px">Источники</h2>
  <ul class="credits">
    <li><a href="https://fujifilm-dsc.com/en/manual/x-s10/menu_shooting/image_quality_setting/" target="_blank" rel="noopener">Инструкция FUJIFILM X-S10: меню качества изображения</a> — список симуляций и их описания</li>
    <li><a href="https://digital-photography-school.com/fujifilm-jpg-film-simulations-guide" target="_blank" rel="noopener">Digital Photography School: Your Guide to the Fujifilm JPG Film Simulations</a></li>
    <li><a href="https://fujixweekly.com/fujifilm-x-trans-iv-recipes/" target="_blank" rel="noopener">Fuji X Weekly: рецепты для X-Trans IV (X-S10)</a> и <a href="https://fujixweekly.com/2024/09/30/which-film-simulation-recipes-when-part-2-x-trans-iv-2024-edition/" target="_blank" rel="noopener">какие рецепты когда</a></li>
    <li><a href="https://www.fujirumors.com/which-film-simulation-is-best-and-worst-for-low-light-photography" target="_blank" rel="noopener">Fuji Rumors: какие симуляции лучше и хуже для темноты</a></li>
  </ul>
  <h2 style="font-size:20px;margin-top:26px">Фотографии</h2>
  <p class="credits">Все фотографии — с Wikimedia Commons, по свободным лицензиям. Схемы и сравнение сделаны для этой страницы.</p>
  <ul class="credits">{''.join(credit_items)}</ul>
</section>
<footer><a class="backlink" href="{MAIN}">← Основы фотографии: ISO, диафрагма, выдержка, фокусное, динамический диапазон</a></footer>
</main>
<script>
(function(){{
  var SIMS={sims_json};
  var CR={json.dumps({k:crs(k) for k in cr if k.startswith(('mill','box','sheep'))},ensure_ascii=False)};
  function $(i){{return document.getElementById(i)}}
  var scene='mill', a='provia', b='classic-chrome', cmp=false;
  var btns=$('simBtns');
  SIMS.forEach(function(s){{
    var bt=document.createElement('button'); bt.type='button'; bt.textContent=s.name.replace(' (+Ye, +R, +G)','').replace(' / Стандарт','').replace(' / Яркий','').replace(' / Мягкий','').replace(' / Кино','');
    if(!s.xs) bt.className='na';
    bt.dataset.k=s.k;
    var timer=null;
    bt.addEventListener('click',function(e){{ if(cmp&&e.shiftKey){{b=s.k}}else{{a=s.k}} upd(); }});
    bt.addEventListener('contextmenu',function(e){{ if(cmp){{e.preventDefault(); b=s.k; upd();}} }});
    bt.addEventListener('touchstart',function(){{ timer=setTimeout(function(){{ if(cmp){{b=s.k; timer='done'; upd();}} }},450); }},{{passive:true}});
    bt.addEventListener('touchend',function(e){{ if(timer==='done'){{e.preventDefault();}} else clearTimeout(timer); timer=null; }});
    btns.appendChild(bt);
  }});
  function sim(k){{for(var i=0;i<SIMS.length;i++) if(SIMS[i].k===k) return SIMS[i];}}
  function upd(){{
    var sa=sim(a), sb=sim(b);
    $('imgA').src='img/'+scene+'-'+a+'.jpg'; $('imgA').alt=sa.name;
    $('imgB').src='img/'+scene+'-'+b+'.jpg'; $('imgB').alt=sb.name;
    $('vstage').style.aspectRatio = scene==='sheep' ? '16/9' : '3/2';
    $('imgB').hidden=!cmp; $('split').hidden=!cmp; $('tagB').hidden=!cmp; $('cmpRow').hidden=!cmp;
    $('tagA').textContent=sa.name+(sa.xs?'':' — нет на X-S10'); $('tagB').textContent=sb.name+(sb.xs?'':' — нет на X-S10');
    $('lblA').textContent=sa.name; $('lblB').textContent=sb.name;
    [].forEach.call(btns.children,function(x){{x.classList.toggle('on',x.dataset.k===a); x.classList.toggle('b-on',cmp&&x.dataset.k===b);}});
    $('vManual').textContent=sa.manual; $('vFilm').textContent=sa.film;
    $('vGood').textContent=sa.xs?sa.good:'—'; $('vTip').textContent=sa.tip;
    $('vCredit').innerHTML=CR[scene+'-'+a+'.jpg']||'';
  }}
  function split(){{var v=$('splitR').value; $('imgB').style.clipPath='inset(0 0 0 '+v+'%)'; $('split').style.left=v+'%';}}
  $('splitR').addEventListener('input',split);
  $('cmpOn').addEventListener('change',function(){{cmp=this.checked; upd(); split();}});
  document.querySelectorAll('#sceneSeg button').forEach(function(x){{x.addEventListener('click',function(){{
    document.querySelectorAll('#sceneSeg button').forEach(function(y){{y.setAttribute('aria-pressed','false')}}); x.setAttribute('aria-pressed','true'); scene=x.dataset.s; upd();
  }})}});
  // drag on stage to move split
  var st=$('vstage'), drag=false;
  function setFromEvent(e){{var r=st.getBoundingClientRect(), x=((e.touches?e.touches[0].clientX:e.clientX)-r.left)/r.width*100; $('splitR').value=Math.max(0,Math.min(100,x)); split();}}
  st.addEventListener('mousedown',function(e){{if(!cmp)return; drag=true; setFromEvent(e);}});
  window.addEventListener('mousemove',function(e){{if(drag) setFromEvent(e);}});
  window.addEventListener('mouseup',function(){{drag=false;}});
  st.addEventListener('touchmove',function(e){{if(cmp) setFromEvent(e);}},{{passive:true}});
  upd(); split();
}})();
</script>
</body>
</html>'''
open('fujisims/index.html','w').write(page)
print('ok', len(page))
