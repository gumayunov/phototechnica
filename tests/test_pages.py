"""Настоящие страницы репозитория собираются без ошибок проверки."""
import unittest

from phototechnica.build import ROOT, list_pages, render
from phototechnica.check import check_page, errors


class RealPagesTest(unittest.TestCase):
    def test_all_pages_check_and_render(self):
        pages = list_pages(ROOT)
        self.assertIn('photo-basics', pages)
        self.assertIn('fujisims', pages)
        for name in pages:
            with self.subTest(page=name):
                self.assertEqual(errors(check_page(name, ROOT)), [])
                self.assertIn('</html>', render(name, ROOT))
