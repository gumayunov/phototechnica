import json
import shutil
import tempfile
import unittest
from pathlib import Path

HEAD = '<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n<title>{{title}}</title>\n'
LAYOUT = '{{shared:head.html}}\n</head>\n<body>\n<main>\n{{section:01-a}}\n</main>\n</body>\n</html>\n'
SECTION = '<section id="a" data-folio-id="a">\n  <h2>Раздел А</h2>\n  <p>Один два три.</p>\n</section>\n'


class TmpRepo(unittest.TestCase):
    """Временный репозиторий с shared/head.html и страницей 'demo'."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.write('shared/head.html', HEAD)
        self.page('demo', {'layout.html': LAYOUT, 'sections/01-a.html': SECTION})

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def page(self, name, files, meta=None, credits=None):
        meta = meta or {'title': 'Демо', 'folio': 'me/demo-x1', 'version': 2}
        self.write(f'pages/{name}/page.json', json.dumps(meta, ensure_ascii=False))
        if credits is not None:
            self.write(f'pages/{name}/credits.json', json.dumps(credits, ensure_ascii=False))
        for rel, text in files.items():
            self.write(f'pages/{name}/{rel}', text)
