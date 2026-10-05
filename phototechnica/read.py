"""Чтение страницы без разбора HTML вручную: outline (структура) и text (чистый текст)."""
import re
from html.parser import HTMLParser

from .build import ROOT, MARKER, BuildError, Page, expand, read_part

BLOCK = {'p', 'div', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'figure', 'figcaption', 'section',
         'header', 'footer', 'table', 'ul', 'ol', 'br', 'details', 'summary', 'aside', 'nav',
         'article', 'blockquote', 'label'}
SKIP = {'script', 'style', 'svg'}
PREFIX = {'h1': '# ', 'h2': '## ', 'h3': '### ', 'h4': '#### ', 'figcaption': '[подпись] ', 'li': '• '}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            if self.skip == 0 and tag == 'svg':
                self.out.append(' [схема] ')
            self.skip += 1
        elif not self.skip:
            if tag in BLOCK:
                self.out.append('\n' + PREFIX.get(tag, ''))
            elif tag in ('td', 'th'):
                self.out.append(' | ')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br' and not self.skip:
            self.out.append('\n')

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        elif not self.skip and tag in BLOCK:
            self.out.append('\n')

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def html_to_text(text):
    p = _Text()
    p.feed(text)
    p.close()
    lines = (re.sub(r'\s+', ' ', l).strip() for l in ''.join(p.out).split('\n'))
    return '\n'.join(l for l in lines if l and l not in ('|', '•'))


def count_words(plain):
    """Слова текста без служебных пометок вида [схема: …] и [подпись]."""
    return len(re.findall(r'\w[\w-]*', re.sub(r'\[[^\]]*\]', ' ', plain)))


def section_names(page):
    return [m.group(2) for m in MARKER.finditer(read_part(page.dir / 'layout.html'))
            if m.group(1) == 'section']


def readable(page, name):
    """Фрагмент раздела с раскрытыми метками; схемы и подписи-атрибуции заменены пометками."""
    def sub(m):
        kind, arg = m.group(1), m.group(2)
        if kind == 'svg':
            return f'[схема: {arg}]'
        if kind == 'cr':
            return ''
        if kind == 'credits':
            return '<li>[список фото из credits.json]</li>'
        if kind == 'url':
            return f'[страница {arg}]'
        return expand(m.group(0), page)
    return MARKER.sub(sub, read_part(page.dir / 'sections' / f'{name}.html'))


def text(name, section=None, root=ROOT):
    page = Page(name, root)
    names = section_names(page)
    if section:
        matched = [n for n in names if n == section or n.split('-', 1)[-1] == section or n[:2] == section]
        if not matched:
            raise BuildError(f'{name}: нет раздела {section}; есть: {", ".join(names)}')
        names = matched
    return '\n\n'.join(f'=== {n}\n' + html_to_text(readable(page, n)) for n in names)


class _Outline(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items, self.cur, self.root_id, self.depth = [], None, None, 0
        self.counts = {'figure': 0, 'table': 0, 'svg': 0}

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in self.counts:
            self.counts[tag] += 1
        fid = d.get('data-folio-id')
        if fid and self.root_id is None:
            self.root_id = fid
        elif fid:
            self.items.append(('id', fid))
        if tag in ('h2', 'h3'):
            self.cur = [tag, '']

    def handle_endtag(self, tag):
        if self.cur and tag == self.cur[0]:
            self.items.append((tag, re.sub(r'\s+', ' ', self.cur[1]).strip()))
            self.cur = None

    def handle_data(self, data):
        if self.cur:
            self.cur[1] += data


def outline(name, root=ROOT):
    page = Page(name, root)
    lines = []
    for n in section_names(page):
        src = readable(page, n)
        o = _Outline()
        o.feed(src.replace('[схема:', '<svg></svg>[схема:'))
        o.close()
        words = count_words(html_to_text(src))
        c = o.counts
        title = next((t for k, t in o.items if k == 'h2'), '')
        lines.append(f'{n}  #{o.root_id or "—"}  {title}  '
                     f'[слов {words}, рисунков {c["figure"]}, таблиц {c["table"]}, схем {c["svg"]}]')
        for kind, value in o.items:
            if kind == 'h3':
                lines.append(f'    ### {value}')
            elif kind == 'id':
                lines.append(f'      #{value}')
    return '\n'.join(lines)
