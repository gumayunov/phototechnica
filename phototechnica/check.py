"""Проверка исходников страницы: вложенность тегов, метки, data-folio-id, картинки."""
from collections import Counter
from fnmatch import fnmatch
from html.parser import HTMLParser
from pathlib import Path
from typing import NamedTuple

from .build import ROOT, BuildError, Page, render, unpublished_links

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'source', 'track', 'wbr'}


class Issue(NamedTuple):
    level: str  # 'error' | 'warning'
    where: str
    message: str

    def __str__(self):
        mark = 'ошибка' if self.level == 'error' else 'предупреждение'
        return f'{mark}: {self.where}: {self.message}'


class _Scan(HTMLParser):
    """Стек открытых тегов, data-folio-id и <img> одного HTML/SVG-текста."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems, self.ids, self.imgs = [], [], [], []

    def _attrs(self, tag, attrs):
        d, line = dict(attrs), self.getpos()[0]
        if 'data-folio-id' in d:
            self.ids.append((d['data-folio-id'], line))
        if tag == 'img':
            self.imgs.append((d, line))

    def handle_starttag(self, tag, attrs):
        self._attrs(tag, attrs)
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        self._attrs(tag, attrs)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        line = self.getpos()[0]
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        elif any(t == tag for t, _ in self.stack):
            while self.stack[-1][0] != tag:
                t, l = self.stack.pop()
                self.problems.append((l, f'<{t}> не закрыт до </{tag}> в строке {line}'))
            self.stack.pop()
        else:
            self.problems.append((line, f'лишний </{tag}>'))

    def finish(self):
        self.close()
        self.problems += [(l, f'<{t}> не закрыт') for t, l in self.stack]
        return self


def scan(text):
    s = _Scan()
    s.feed(text)
    return s.finish()


def check_page(name, root=ROOT):
    root = Path(root)
    try:
        page = Page(name, root)
    except BuildError as e:
        return [Issue('error', name, str(e))]
    issues = []
    # разделы и схемы сбалансированы сами по себе — ошибка указывает на файл и строку
    for path in sorted(page.dir.glob('sections/*.html')) + sorted(page.dir.glob('svg/*.svg')):
        for line, msg in scan(path.read_text(encoding='utf-8')).problems:
            issues.append(Issue('error', f'{path.relative_to(root)}:{line}', msg))
    try:
        text = render(name, root)
    except BuildError as e:
        return issues + [Issue('error', name, str(e))]
    where = f'pages/{name} (собранная страница)'
    if '{{' in text:
        line = text[:text.index('{{')].count('\n') + 1
        issues.append(Issue('error', f'{where}:{line}', 'нераспознанная метка: ' + text[text.index('{{'):][:40]))
    for other in unpublished_links(text):
        issues.append(Issue('warning', where, f'ссылка на неопубликованную страницу {other} — '
                                              f'заработает после ./pt publish {other}'))
    s = scan(text)
    if not issues:
        issues += [Issue('error', f'{where}:{l}', m) for l, m in s.problems]
    for fid, n in Counter(i for i, _ in s.ids).items():
        if n > 1:
            issues.append(Issue('error', where, f'data-folio-id="{fid}" встречается {n} раза'))
    for attrs, line in s.imgs:
        src = attrs.get('src', '')
        if 'alt' not in attrs:
            issues.append(Issue('error', f'{where}:{line}', f'<img src="{src}"> без alt'))
        if src and not src.startswith(('http://', 'https://', 'data:')) and not (page.dir / src).exists():
            issues.append(Issue('error', f'{where}:{line}', f'нет файла {src}'))
    dynamic = page.meta.get('dynamic_img', [])  # картинки, чьи имена собирает JS
    for img in sorted((page.dir / 'img').glob('*')):
        if img.name.startswith('.') or not img.is_file():
            continue
        where_img = f'pages/{name}/img/{img.name}'
        if img.name not in text and not any(fnmatch(img.name, p) for p in dynamic):
            issues.append(Issue('warning', where_img, 'картинка нигде не используется'))
        if img.name not in page.credits:
            issues.append(Issue('warning', where_img, 'нет атрибуции в credits.json'))
    return issues


def errors(issues):
    return [i for i in issues if i.level == 'error']
