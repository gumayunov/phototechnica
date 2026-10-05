import json

from phototechnica.build import BuildError, render
from phototechnica.check import check_page
from phototechnica.scaffold import new_page
from tests.helpers import TmpRepo


class NewPageTest(TmpRepo):
    def test_new_page_builds_clean(self):
        self.write('shared/base.css', 'body{}\n')
        page_dir = new_page('lenses', 'Объективы', self.root)
        self.assertEqual(json.loads((page_dir / 'page.json').read_text(encoding='utf-8')),
                         {'title': 'Объективы', 'folio': '', 'version': 0})
        self.assertEqual(check_page('lenses', self.root), [])
        self.assertIn('<h1>Объективы</h1>', render('lenses', self.root))

    def test_rejects_bad_slug_and_existing(self):
        for slug in ['Lenses', 'my_page', '-x', 'demo']:
            with self.subTest(slug=slug), self.assertRaises(BuildError):
                new_page(slug, 'X', self.root)
