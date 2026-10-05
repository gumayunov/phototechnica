from phototechnica.check import check_page, errors
from tests.helpers import TmpRepo


class CheckTest(TmpRepo):
    def messages(self, level='error'):
        return [f'{i.where}: {i.message}' for i in check_page('demo', self.root) if i.level == level]

    def section(self, text):
        self.write('pages/demo/sections/01-a.html', text)

    def test_clean_page(self):
        self.assertEqual(check_page('demo', self.root), [])

    def test_unclosed_tag_points_to_file_and_line(self):
        self.section('<section data-folio-id="a">\n  <p>раз\n  <div>два</div>\n</section>\n')
        self.assertEqual(self.messages(), ['pages/demo/sections/01-a.html:2: <p> не закрыт до </section> в строке 4'])

    def test_extra_close_and_unclosed_at_end(self):
        self.section('<div></span></div>\n<b>\n')
        self.assertEqual(self.messages(), ['pages/demo/sections/01-a.html:1: лишний </span>',
                                           'pages/demo/sections/01-a.html:2: <b> не закрыт'])

    def test_svg_self_closing_and_void_tags_are_fine(self):
        self.write('pages/demo/svg/s.svg', '<svg><path d="M0 0"/><g><rect/></g></svg>\n')
        self.section('<figure>{{svg:s}}<img src="https://x/y.jpg" alt=""><br></figure>\n')
        self.assertEqual(self.messages(), [])

    def test_broken_svg_file(self):
        self.write('pages/demo/svg/s.svg', '<svg><g></svg>\n')
        self.section('<figure>{{svg:s}}</figure>\n')
        self.assertEqual(self.messages(), ['pages/demo/svg/s.svg:1: <g> не закрыт до </svg> в строке 1'])

    def test_layout_problem_reported_on_rendered_page(self):
        self.write('pages/demo/layout.html', '{{shared:head.html}}\n</head>\n<body>\n<main>\n{{section:01-a}}\n</body>\n</html>\n')
        self.assertEqual(self.messages(), ['pages/demo (собранная страница):8: <main> не закрыт до </body> в строке 13'])

    def test_build_error_is_reported(self):
        self.section('<p>{{svg:nope}}</p>\n')
        self.assertEqual(self.messages(), ['demo: demo: {{svg:nope}} — нет файла pages/demo/svg/nope.svg'])

    def test_unrecognised_marker(self):
        self.section('<p>{{ svg:x }}</p>\n')
        self.assertEqual(len(self.messages()), 1)
        self.assertIn('нераспознанная метка: {{ svg:x }}', self.messages()[0])

    def test_duplicate_folio_id(self):
        self.section('<section data-folio-id="a"><p data-folio-id="a">x</p></section>\n')
        self.assertIn('pages/demo (собранная страница): data-folio-id="a" встречается 2 раза', self.messages())

    def test_img_without_alt_and_missing_file(self):
        self.section('<p><img src="img/none.jpg"></p>\n')
        msgs = self.messages()
        self.assertTrue(any('<img src="img/none.jpg"> без alt' in m for m in msgs), msgs)
        self.assertTrue(any('нет файла img/none.jpg' in m for m in msgs), msgs)

    def test_unused_image_warning_and_dynamic_img(self):
        self.write('pages/demo/img/used.jpg', 'x')
        self.write('pages/demo/img/unused.jpg', 'x')
        self.write('pages/demo/img/zoom-1.jpg', 'x')
        self.section('<p><img src="img/used.jpg" alt="u"></p>\n')
        cr = {'title': 't', 'page': 'p', 'license': 'CC0', 'artist': 'a', 'author': 'a'}
        self.page('demo', {}, meta={'title': 'Демо', 'folio': '', 'version': 0, 'dynamic_img': ['zoom-*.jpg']},
                  credits={'used.jpg': cr, 'unused.jpg': cr, 'zoom-1.jpg': cr})
        self.assertEqual(self.messages(), [])
        self.assertEqual(self.messages('warning'), ['pages/demo/img/unused.jpg: картинка нигде не используется'])
        self.assertEqual(errors(check_page('demo', self.root)), [])

    CR = {'title': 't', 'page': 'p', 'license': 'CC0', 'artist': 'a', 'author': 'a'}

    def test_credited_used_image_has_no_warning(self):
        self.write('pages/demo/img/used.jpg', 'x')
        self.section('<p><img src="img/used.jpg" alt="u"></p>\n')
        self.page('demo', {}, credits={'used.jpg': self.CR})
        self.assertEqual(self.messages('warning'), [])

    def test_uncredited_image_warning(self):
        self.write('pages/demo/img/used.jpg', 'x')
        self.section('<p><img src="img/used.jpg" alt="u"></p>\n')
        self.assertEqual(self.messages('warning'), ['pages/demo/img/used.jpg: нет атрибуции в credits.json'])
        self.assertEqual(errors(check_page('demo', self.root)), [])

    def test_hidden_files_and_dirs_in_img_are_skipped(self):
        self.write('pages/demo/img/.DS_Store', 'x')
        (self.root / 'pages/demo/img/sub').mkdir()
        self.assertEqual(self.messages('warning'), [])

    def test_link_to_unpublished_page_is_a_warning(self):
        self.page('other', {'layout.html': 'x\n'}, meta={'title': 'O', 'folio': '', 'version': 0})
        self.section('<p><a href="{{url:other}}">o</a></p>\n')
        self.assertEqual(self.messages(), [])
        self.assertEqual(self.messages('warning'), [
            'pages/demo (собранная страница): ссылка на неопубликованную страницу other — '
            'заработает после ./pt publish other'])

    def test_missing_page(self):
        self.assertIn('нет страницы nope', str(check_page('nope', self.root)[0]))
