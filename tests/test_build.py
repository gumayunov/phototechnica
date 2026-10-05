from phototechnica.build import BuildError, build_page, render
from tests.helpers import TmpRepo

CREDIT = {'a.jpg': {'title': 'A.jpg', 'page': 'https://commons.wikimedia.org/wiki/File:A.jpg',
                    'license': 'CC0', 'artist': 'raw <b>', 'author': 'Аня & Co'}}


class RenderTest(TmpRepo):
    def test_layout_head_and_section(self):
        out = render('demo', self.root)
        self.assertTrue(out.startswith('<!doctype html>\n<html lang="ru">'))
        self.assertIn('<title>Демо</title>\n</head>', out)
        self.assertIn('<main>\n<section id="a"', out)
        self.assertTrue(out.endswith('</html>'))  # один завершающий \n файла отрезан

    def test_part_keeps_inner_newlines(self):
        self.write('pages/demo/sections/01-a.html', '<p>x</p>\n\n')
        self.assertIn('<main>\n<p>x</p>\n\n</main>', render('demo', self.root))

    def test_nested_markers_in_section_svg_js(self):
        self.page('demo', {'sections/01-a.html': '<figure>{{svg:s}}</figure>\n',
                           'svg/s.svg': '<svg><text>{{title}}</text></svg>\n'})
        self.assertIn('<figure><svg><text>Демо</text></svg></figure>', render('demo', self.root))

    def test_cr_and_credits(self):
        self.page('demo', {'sections/01-a.html': '<p>{{cr:a.jpg}}</p>\n<ul>\n{{credits}}\n</ul>\n'},
                  credits=CREDIT)
        out = render('demo', self.root)
        self.assertIn('<span class="cr">Фото: <a href="https://commons.wikimedia.org/wiki/File:A.jpg" '
                      'target="_blank" rel="noopener">Аня &amp; Co</a>, CC0, Wikimedia Commons</span>', out)
        self.assertIn('<ul>\n    <li><a href="https://commons.wikimedia.org/wiki/File:A.jpg" target="_blank" '
                      'rel="noopener">A.jpg</a> — Аня &amp; Co, CC0</li>\n</ul>', out)

    def test_url_of_other_page(self):
        self.page('other', {'layout.html': 'x\n'}, meta={'title': 'O', 'folio': 'me/other-y2', 'version': 1})
        self.page('demo', {'sections/01-a.html': '<a href="{{url:other}}">o</a>\n'})
        self.assertIn('href="https://folio.fold-core.ru/a/me/other-y2/"', render('demo', self.root))

    def test_gen(self):
        self.page('demo', {'sections/01-a.html': '<div>{{gen:cards}}</div>\n',
                           'gen.py': 'def generate(page):\n    return {"cards": "<i>{{svg:x}}</i>"}\n'})
        # значение gen не раскрывается повторно
        self.assertIn('<div><i>{{svg:x}}</i></div>', render('demo', self.root))

    def test_errors(self):
        cases = {
            '{{svg:nope}}': 'нет файла pages/demo/svg/nope.svg',
            '{{cr:nope.jpg}}': 'нет атрибуции для nope.jpg',
            '{{url:nope}}': 'нет страницы nope',
            '{{gen:nope}}': 'gen.py не вернул такую метку',
            '{{bogus:x}}': 'неизвестная метка',
            '{{svg}}': 'нет аргумента',
        }
        for marker, msg in cases.items():
            with self.subTest(marker=marker):
                self.write('pages/demo/sections/01-a.html', f'<p>{marker}</p>\n')
                with self.assertRaises(BuildError) as cm:
                    render('demo', self.root)
                self.assertIn(msg, str(cm.exception))

    def test_unpublished_url(self):
        self.page('other', {'layout.html': 'x\n'}, meta={'title': 'O', 'folio': '', 'version': 0})
        self.write('pages/demo/sections/01-a.html', '<a href="{{url:other}}#part">o</a>\n')
        self.assertIn('<a href="#unpublished-other#part">o</a>', render('demo', self.root))

    def test_recursion_limit(self):
        self.write('pages/demo/sections/01-a.html', '{{section:01-a}}\n')
        with self.assertRaisesRegex(BuildError, 'глубже'):
            render('demo', self.root)


class BuildPageTest(TmpRepo):
    def test_writes_index_and_copies_img(self):
        self.write('pages/demo/img/a.jpg', 'JPG')
        stale = self.write('dist/demo/old.txt', 'x')
        index = build_page('demo', self.root)
        self.assertEqual(index, self.root / 'dist/demo/index.html')
        self.assertEqual(index.read_bytes(), render('demo', self.root).encode())
        self.assertEqual((self.root / 'dist/demo/img/a.jpg').read_text(), 'JPG')
        self.assertFalse(stale.exists())
