"""Сборка страниц: layout.html страницы + раскрытие меток {{вид:аргумент}}."""
import html
import importlib.util
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLIO_BASE = 'https://folio.fold-core.ru/a/'
UNPUBLISHED = '#unpublished-'  # адрес-заглушка для {{url:…}} неопубликованной страницы
MARKER = re.compile(r'\{\{([a-z]+)(?::([^{}\s]+))?\}\}')
# метка → (каталог страницы, расширение); содержимое таких файлов раскрывается дальше
PAGE_FILES = {'section': ('sections', '.html'), 'svg': ('svg', '.svg'),
              'js': ('js', '.js'), 'css': ('css', '.css')}
MAX_DEPTH = 8


class BuildError(Exception):
    pass


def read_part(path):
    """Содержимое файла-фрагмента без одного завершающего перевода строки."""
    text = Path(path).read_text(encoding='utf-8')
    return text[:-1] if text.endswith('\n') else text


def folio_url(folio_id):
    return f'{FOLIO_BASE}{folio_id}/'


def list_pages(root=ROOT):
    return sorted(p.parent.name for p in (Path(root) / 'pages').glob('*/page.json'))


class Page:
    def __init__(self, name, root=ROOT):
        self.name = name
        self.root = Path(root)
        self.dir = self.root / 'pages' / name
        meta = self.dir / 'page.json'
        if not meta.exists():
            raise BuildError(f'нет страницы {name}: не найден {meta}')
        self.meta = json.loads(meta.read_text(encoding='utf-8'))
        credits = self.dir / 'credits.json'
        self.credits = json.loads(credits.read_text(encoding='utf-8')) if credits.exists() else {}
        self._gen = None

    def gen(self):
        """Метки {{gen:…}} из gen.py страницы: generate(page) -> dict[str, str]."""
        if self._gen is None:
            path = self.dir / 'gen.py'
            if path.exists():
                spec = importlib.util.spec_from_file_location(f'gen_{self.name.replace("-", "_")}', path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self._gen = mod.generate(self)
            else:
                self._gen = {}
        return self._gen

    def cr(self, img):
        c = self.credits.get(img)
        if c is None:
            raise BuildError(f'{self.name}: нет атрибуции для {img} в credits.json')
        return (f'<span class="cr">Фото: <a href="{html.escape(c["page"])}" target="_blank" rel="noopener">'
                f'{html.escape(c["author"])}</a>, {html.escape(c["license"])}, Wikimedia Commons</span>')

    def credits_list(self):
        seen, items = set(), []
        for c in self.credits.values():
            if c['page'] in seen:
                continue
            seen.add(c['page'])
            items.append(f'    <li><a href="{html.escape(c["page"])}" target="_blank" rel="noopener">'
                         f'{html.escape(c["title"])}</a> — {html.escape(c["author"])}, {html.escape(c["license"])}</li>')
        return '\n'.join(items)


def resolve(page, kind, arg):
    """Значение метки и нужно ли раскрывать метки внутри него."""
    if kind in PAGE_FILES or kind == 'shared':
        if not arg:
            raise BuildError(f'{page.name}: у метки {{{{{kind}}}}} нет аргумента')
        if kind == 'shared':
            path = page.root / 'shared' / arg
        else:
            sub, ext = PAGE_FILES[kind]
            path = page.dir / sub / (arg + ext)
        if not path.exists():
            raise BuildError(f'{page.name}: {{{{{kind}:{arg}}}}} — нет файла {path.relative_to(page.root)}')
        return read_part(path), True
    if kind == 'cr':
        return page.cr(arg), False
    if kind == 'credits':
        return page.credits_list(), False
    if kind == 'title':
        return html.escape(page.meta['title']), False
    if kind == 'url':
        other = Page(arg, page.root)
        if not other.meta.get('folio'):
            return UNPUBLISHED + arg, False
        return folio_url(other.meta['folio']), False
    if kind == 'gen':
        values = page.gen()
        if arg not in values:
            raise BuildError(f'{page.name}: {{{{gen:{arg}}}}} — gen.py не вернул такую метку')
        return values[arg], False
    raise BuildError(f'{page.name}: неизвестная метка {{{{{kind}}}}}')


def expand(text, page, depth=0):
    if depth > MAX_DEPTH:
        raise BuildError(f'{page.name}: метки вложены глубже {MAX_DEPTH} уровней')

    def sub(m):
        value, nested = resolve(page, m.group(1), m.group(2))
        return expand(value, page, depth + 1) if nested else value

    return MARKER.sub(sub, text)


def unpublished_links(text):
    """Страницы, на которые собранный текст ссылается до их публикации."""
    return sorted(set(re.findall(re.escape(UNPUBLISHED) + r'([a-z0-9-]+)', text)))


def render(name, root=ROOT):
    page = Page(name, root)
    return expand(read_part(page.dir / 'layout.html'), page)


def build_page(name, root=ROOT, out=None):
    """Собрать dist/<name>/index.html и img/; вернуть путь к index.html."""
    root = Path(root)
    out = Path(out) if out else root / 'dist'
    text = render(name, root)
    dest = out / name
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    with open(dest / 'index.html', 'w', encoding='utf-8', newline='') as f:
        f.write(text)
    img = root / 'pages' / name / 'img'
    if img.exists():
        shutil.copytree(img, dest / 'img')
    return dest / 'index.html'
