"""Разовый перенос: legacy/template.html и legacy/build_fs.py → pages/*, shared/*.

Запуск из корня репозитория: python3 tools/migrate.py
После переноса ./pt build должен дать файлы, равные tests/baseline/*/index.html.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / 'legacy'
FOLIO = {
    'photo-basics': 'bernhard/osnovy-fotografii-iso-f-vyderzhka-fokusn-fe0kh3se',
    'fujisims': 'bernhard/simulyatsii-plenki-fujifilm-x-s10-kejiswf8',
}
VERSION = {'photo-basics': 5, 'fujisims': 1}
TITLE = {'photo-basics': 'Основы фотографии', 'fujisims': 'Симуляции плёнки X-S10'}
# имена схем основной страницы по порядку появления
PB_SVG = ['light-path', 'bucket', 'aperture-scale', 'shutter-scale', 'iso-scale', 'triangle',
          'exposure-sim-scene', 'focus-plane', 'focus-sim-rays', 'focus-sim-view', 'af-contrast',
          'af-phase', 'focal-magnifier', 'focal-angle', 'focal-real-lens', 'focal-fov',
          'normal-lens', 'dr-bars', 'histograms', 'relationship-map']
# комментарий верхнего уровня в скрипте основной страницы → имя js-файла
PB_JS = {'DOF tabs': 'dof-tabs', 'Sunflower petals': 'sunflower', 'Simulator': 'exposure-sim',
         'Focus simulator': 'focus-sim', 'Face perspective demo': 'face-perspective',
         'Side TOC': 'toc', 'Focal slider': 'focal-slider'}
PB_AUTHORS = {'fir0002': 'fir0002 (flagstaffotos)', 'Kevin McCoy': 'Kevin McCoy', 'Daniel Schwen': 'Daniel Schwen',
              'Kübelbeck': 'Armin Kübelbeck', 'Hutton': 'Andrew Hutton', 'HuttyMcphoo': 'Andrew Hutton'}
FS_AUTHORS = {'Ziko': 'Ziko van Dijk', 'torstenbehrens': 'Torsten Behrens', 'Torsten Behrens': 'Torsten Behrens',
              'tsuruta': 'tsuruta yosuke', 'Trolle': 'Kristoffer Trolle', 'Dambr': 'Kārlis Dambrāns'}


def url(page):
    return f'https://folio.fold-core.ru/a/{FOLIO[page]}/'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(text)


def take(text, start, end, marker, dest):
    """Вынести text[start:end] в файл dest, оставив на его месте метку.

    Перевод строки в начале и в конце куска остаётся в layout вокруг метки; файл
    получает середину и один завершающий перевод строки, который сборка отрезает.
    """
    part = text[start:end]
    lead = '\n' if part.startswith('\n') else ''
    trail = '\n' if part.endswith('\n') and len(part) > len(lead) else ''
    core = part[len(lead):len(part) - len(trail)]
    write(dest, core + '\n')
    return text[:start] + lead + marker + trail + text[end:]


def take_svgs(text, names, out_dir):
    """Вынести все <svg>…</svg> в out_dir/<имя>.svg; names расходуются по порядку."""
    while True:
        m = re.search(r'<svg\b', text)
        if not m:
            return text
        end = text.index('</svg>', m.start()) + len('</svg>')
        assert '<svg' not in text[m.start() + 4:end], 'вложенный <svg> не поддерживается'
        text = take(text, m.start(), end, '{{svg:%s}}' % names[0], out_dir / f'{names[0]}.svg')
        names.pop(0)


def line_starts(text):
    starts, pos = [], 0
    for line in text.splitlines(keepends=True):
        starts.append(pos)
        pos += len(line)
    return starts


def take_sections(text, page_dir):
    """Hero (от <main> до первой секции) и секции → sections/NN-имя.html."""
    starts = line_starts(text)
    lines = text.splitlines(keepends=True)
    main = next(i for i, l in enumerate(lines) if l.startswith('<main>'))
    footer = next(i for i, l in enumerate(lines) if l.startswith('<footer'))
    sec = [i for i, l in enumerate(lines) if l.startswith('<section')]
    cuts = []
    for i in sec:
        j = i - 1 if lines[i - 1].startswith('<!--') else i
        name = re.search(r'(?:\bid|data-folio-id)="([^"]+)"', lines[i]).group(1)
        cuts.append((j, name))
    chunks = [(main + 1, cuts[0][0], 'hero')]
    for k, (j, name) in enumerate(cuts):
        chunks.append((j, cuts[k + 1][0] if k + 1 < len(cuts) else footer, name))
    for n, (a, b, name) in reversed(list(enumerate(chunks))):
        fname = f'{n:02d}-{name}'
        text = take(text, starts[a], starts[b], '{{section:%s}}' % fname, page_dir / 'sections' / f'{fname}.html')
    return text


def take_head_and_css(text, title, page_dir):
    """Шапку до <style> — в shared/head.html, стили — в shared/base.css (+ css/page.css)."""
    s = text.index('<style>')
    head = text[:s].replace(f'<title>{title}</title>', '<title>{{title}}</title>')
    shared_head = ROOT / 'shared' / 'head.html'
    if shared_head.exists():
        assert shared_head.read_text(encoding='utf-8') == head, 'шапки страниц различаются'
    text = take(head, 0, len(head), '{{shared:head.html}}', shared_head) + text[s:]
    a = text.index('<style>') + len('<style>')
    b = text.index('</style>')
    css = text[a:b]
    base_path = ROOT / 'shared' / 'base.css'
    if not base_path.exists():
        return take(text, a, b, '{{shared:base.css}}', base_path)
    base = '\n' + base_path.read_text(encoding='utf-8')
    assert css.startswith(base), 'стили страницы не начинаются с shared/base.css'
    text = take(text, a + len(base), b, '{{css:page}}', page_dir / 'css' / 'page.css')
    return text[:a] + '\n{{shared:base.css}}\n' + text[a + len(base):]


def with_authors(credits, authors):
    out = {}
    for name, c in credits.items():
        author = next((v for k, v in authors.items() if k in c['artist']), c['artist'].strip())
        out[name] = {**c, 'author': author}
    return out


def write_page_json(page, page_dir):
    meta = {'title': TITLE[page], 'folio': FOLIO[page], 'version': VERSION[page]}
    if page == 'photo-basics':
        meta['dynamic_img'] = ['focal-*.jpg']
    write(page_dir / 'page.json', json.dumps(meta, ensure_ascii=False, indent=2) + '\n')


def migrate_photo_basics():
    page_dir = ROOT / 'pages' / 'photo-basics'
    text = (LEGACY / 'template.html').read_text(encoding='utf-8')
    text = text.replace('{{CREDITS}}', '{{credits}}').replace(url('fujisims'), '{{url:fujisims}}')
    text = take_head_and_css(text, TITLE['photo-basics'], page_dir)
    a = text.index('<script>\n(function(){\n') + len('<script>\n(function(){\n')
    b = text.index('})();\n</script>')
    starts = [a + m.start() for m in re.finditer(r'^  // (.+)$', text[a:b], re.M)]
    labels = re.findall(r'^  // (.+)$', text[a:b], re.M)
    assert a == starts[0] and [PB_JS[l] for l in labels] == list(PB_JS.values()), labels
    bounds = list(zip(starts, starts[1:] + [b], labels))
    for s, e, label in reversed(bounds):
        text = take(text, s, e, '{{js:%s}}' % PB_JS[label], page_dir / 'js' / f'{PB_JS[label]}.js')
    svg_names = list(PB_SVG)
    text = take_svgs(text, svg_names, page_dir / 'svg')
    assert not svg_names, f'не нашлись схемы: {svg_names}'
    text = take_sections(text, page_dir)
    write(page_dir / 'layout.html', text + '\n')
    credits = json.loads((LEGACY / 'credits.json').read_text(encoding='utf-8'))
    write(page_dir / 'credits.json',
          json.dumps(with_authors(credits, PB_AUTHORS), ensure_ascii=False, indent=1) + '\n')
    write_page_json('photo-basics', page_dir)


def legacy_fujisims():
    """Выполнить legacy/build_fs.py без записи файла и вернуть его переменные."""
    src = (LEGACY / 'build_fs.py').read_text(encoding='utf-8')
    src = src.replace("open('fujisims/index.html','w').write(page)", '')
    src = src.replace("open('template.html')", f"open({str(LEGACY / 'template.html')!r})")
    src = src.replace("open('fs_credits.json')", f"open({str(LEGACY / 'fs_credits.json')!r})")
    ns = {}
    exec(compile(src, 'build_fs.py', 'exec'), ns)
    return ns


def replace_once(text, old, new):
    assert text.count(old) == 1, (new, text.count(old))
    return text.replace(old, new)


def migrate_fujisims():
    page_dir = ROOT / 'pages' / 'fujisims'
    ns = legacy_fujisims()
    text = ns['page']
    cr_json = json.dumps({k: ns['crs'](k) for k in ns['cr'] if k.startswith(('mill', 'box', 'sheep'))},
                         ensure_ascii=False)
    text = replace_once(text, 'var SIMS=' + ns['sims_json'] + ';', 'var SIMS={{gen:sims-json}};')
    text = replace_once(text, 'var CR=' + cr_json + ';', 'var CR={{gen:cr-json}};')
    text = replace_once(text, ns['cards'], '{{gen:sim-cards}}')
    text = replace_once(text, ''.join(ns['credit_items']), '{{gen:credit-list}}')
    text = text.replace(ns['MAIN'], '{{url:photo-basics}}')
    for name in ns['cr']:
        text = text.replace(ns['crs'](name), '{{cr:%s}}' % name)
    text = take_head_and_css(text, TITLE['fujisims'], page_dir)
    a = text.index('<script>\n') + len('<script>\n')
    b = text.index('\n</script>')
    text = take(text, a, b + 1, '{{js:viewer}}', page_dir / 'js' / 'viewer.js')
    svg_names = ['bw-filters']
    text = take_svgs(text, svg_names, page_dir / 'svg')
    assert not svg_names
    text = take_sections(text, page_dir)
    write(page_dir / 'layout.html', text + '\n')
    sims = [dict(s) for s in ns['SIMS']]
    write(page_dir / 'data' / 'sims.json', json.dumps(sims, ensure_ascii=False, indent=1) + '\n')
    credits = json.loads((LEGACY / 'fs_credits.json').read_text(encoding='utf-8'))
    write(page_dir / 'credits.json',
          json.dumps(with_authors(credits, FS_AUTHORS), ensure_ascii=False, indent=1) + '\n')
    write_page_json('fujisims', page_dir)


if __name__ == '__main__':
    migrate_photo_basics()
    migrate_fujisims()
    print('ok')
