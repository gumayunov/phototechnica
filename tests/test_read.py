from phototechnica.build import BuildError
from phototechnica.read import count_words, html_to_text, outline, text
from tests.helpers import TmpRepo

SECTION = '''<section id="focus" data-folio-id="focus">
  <span class="sec-num">06</span>
  <h2>Фокусировка</h2>
  <p>Объектив <b>наводится</b> на одно расстояние.</p>
  <figure data-folio-id="plane">{{svg:plane}}<figcaption>Плоскость резкости.{{cr:a.jpg}}</figcaption></figure>
  <h3>Режимы</h3>
  <table data-folio-id="modes"><tr><th>Режим</th><th>Когда</th></tr><tr><td>AF-S</td><td>портрет</td></tr></table>
  <script>var x = "<p>не текст</p>";</script>
</section>
'''
CREDIT = {'a.jpg': {'title': 'A.jpg', 'page': 'https://c/A', 'license': 'CC0', 'artist': 'A', 'author': 'A'}}


class ReadTest(TmpRepo):
    def setUp(self):
        super().setUp()
        self.page('demo', {'layout.html': '{{shared:head.html}}\n<main>\n{{section:01-a}}\n{{section:02-focus}}\n</main>\n',
                           'sections/02-focus.html': SECTION,
                           'svg/plane.svg': '<svg><text>подпись схемы</text></svg>\n'},
                  credits=CREDIT)

    def test_text_of_section(self):
        self.assertEqual(text('demo', '02', self.root),
                         '=== 02-focus\n06\n## Фокусировка\nОбъектив наводится на одно расстояние.\n'
                         '[схема: plane]\n[подпись] Плоскость резкости.\n### Режимы\n'
                         '| Режим | Когда\n| AF-S | портрет')

    def test_section_by_name_and_whole_page(self):
        self.assertEqual(text('demo', 'focus', self.root), text('demo', '02-focus', self.root))
        whole = text('demo', None, self.root)
        self.assertTrue(whole.startswith('=== 01-a\n## Раздел А\nОдин два три.\n\n=== 02-focus\n'))

    def test_unknown_section(self):
        with self.assertRaisesRegex(BuildError, 'нет раздела 07; есть: 01-a, 02-focus'):
            text('demo', '07', self.root)

    def test_outline(self):
        self.assertEqual(outline('demo', self.root),
                         '01-a  #a  Раздел А  [слов 5, рисунков 0, таблиц 0, схем 0]\n'
                         '02-focus  #focus  Фокусировка  [слов 14, рисунков 1, таблиц 1, схем 1]\n'
                         '      #plane\n'
                         '    ### Режимы\n'
                         '      #modes')

    def test_inline_svg_is_marked(self):
        self.assertEqual(html_to_text('<p>до<svg><text>x</text></svg>после</p>'), 'до [схема] после')

    def test_count_words_skips_service_marks(self):
        self.assertEqual(count_words('## Заголовок\n[схема: a-b] [подпись] Два слова | AF-S'), 4)
