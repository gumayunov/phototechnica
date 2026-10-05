"""Заготовка новой страницы: ./pt new <slug> --title "…"."""
import json
import re

from .build import ROOT, BuildError

LAYOUT = '''{{shared:head.html}}
<style>
{{shared:base.css}}
</style>
</head>
<body>
<main>
{{section:00-hero}}
{{section:01-start}}
{{section:99-credits}}
</main>
</body>
</html>
'''
HERO = '''<header class="hero" data-folio-id="intro">
  <h1>{{title}}</h1>
  <p class="lead">Вступление.</p>
</header>

'''
START = '''<section id="start" data-folio-id="start">
  <span class="sec-num">01</span>
  <h2>Первый раздел</h2>
  <p>Текст раздела.</p>
</section>

'''
CREDITS = '''<section data-folio-id="credits">
  <h2 style="font-size:20px">Фотографии</h2>
  <p class="credits">Все фотографии взяты с Wikimedia Commons и распространяются по свободным лицензиям.</p>
  <ul class="credits">
{{credits}}
  </ul>
</section>
'''


def new_page(slug, title, root=ROOT):
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', slug):
        raise BuildError(f'имя страницы {slug!r}: только латиница в нижнем регистре, цифры и дефисы')
    page_dir = root / 'pages' / slug
    if page_dir.exists():
        raise BuildError(f'страница {slug} уже есть: {page_dir}')
    (page_dir / 'sections').mkdir(parents=True)
    (page_dir / 'img').mkdir()
    (page_dir / 'page.json').write_text(
        json.dumps({'title': title, 'folio': '', 'version': 0}, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8')
    (page_dir / 'credits.json').write_text('{}\n', encoding='utf-8')
    (page_dir / 'layout.html').write_text(LAYOUT, encoding='utf-8')
    for name, text in [('00-hero', HERO), ('01-start', START), ('99-credits', CREDITS)]:
        (page_dir / 'sections' / f'{name}.html').write_text(text, encoding='utf-8')
    return page_dir
