import json
import os
import stat

from phototechnica.folio import PublishError, publish
from tests.helpers import TmpRepo

FAKE = '''#!/bin/sh
echo "$@" > "{log}"
{body}
'''


class PublishTest(TmpRepo):
    def fake(self, body):
        self.log = self.root / 'folio.log'
        path = self.write('fake-folio', FAKE.format(log=self.log, body=body))
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
        return str(path)

    def meta(self):
        return json.loads((self.root / 'pages/demo/page.json').read_text(encoding='utf-8'))

    def test_update_existing_with_base(self):
        folio = self.fake('echo "folio: скилл устарел" >&2\n'
                          'echo \'{"id":"me/demo-x1","owner":"me","url":"https://f/a/me/demo-x1/","version":3}\'')
        info = publish('demo', self.root, folio)
        self.assertEqual(info['version'], 3)
        self.assertEqual(self.log.read_text().split(),
                         ['update', 'me/demo-x1', str(self.root / 'dist/demo'), '--base', '2'])
        self.assertEqual(self.meta(), {'title': 'Демо', 'folio': 'me/demo-x1', 'version': 3})

    def test_first_publish_records_id(self):
        self.page('demo', {}, meta={'title': 'Демо', 'folio': '', 'version': 0})
        folio = self.fake('echo \'{"id":"me/demo-new","url":"https://f/a/me/demo-new/","version":1}\'')
        publish('demo', self.root, folio)
        self.assertEqual(self.log.read_text().split(), ['publish', str(self.root / 'dist/demo'), '--title', 'Демо'])
        self.assertEqual(self.meta(), {'title': 'Демо', 'folio': 'me/demo-new', 'version': 1})

    def test_conflict_keeps_page_json(self):
        folio = self.fake('echo \'folio: HTTP 409: {"error": "base 2 != latest 4", "code": "conflict"}\' >&2\nexit 1')
        with self.assertRaisesRegex(PublishError, 'HTTP 409(.|\n)*folio info me/demo-x1'):
            publish('demo', self.root, folio)
        self.assertEqual(self.meta()['version'], 2)

    def test_check_errors_stop_before_folio(self):
        self.write('pages/demo/sections/01-a.html', '<p>{{svg:nope}}</p>\n')
        folio = self.fake('exit 0')
        with self.assertRaisesRegex(PublishError, 'проверка не прошла'):
            publish('demo', self.root, folio)
        self.assertFalse(self.log.exists())
