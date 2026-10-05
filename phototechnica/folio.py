"""Публикация собранной страницы на folio через CLI скилла fc-folio."""
import json
import os
import subprocess
from pathlib import Path

from .build import ROOT, BuildError, Page, build_page
from .check import check_page, errors

FOLIO_BIN = os.environ.get('PT_FOLIO', str(Path.home() / '.claude/skills/fc-folio/scripts/folio'))


class PublishError(Exception):
    pass


def publish(name, root=ROOT, folio_bin=None):
    """check → build → folio update (или publish для новой страницы); обновляет page.json."""
    folio_bin = folio_bin or FOLIO_BIN
    bad = errors(check_page(name, root))
    if bad:
        raise PublishError('проверка не прошла:\n' + '\n'.join(map(str, bad)))
    index = build_page(name, root)
    page = Page(name, root)
    if page.meta.get('folio'):
        cmd = [folio_bin, 'update', page.meta['folio'], str(index.parent)]
        if page.meta.get('version'):
            cmd += ['--base', str(page.meta['version'])]
    else:
        cmd = [folio_bin, 'publish', str(index.parent), '--title', page.meta['title']]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        msg = (res.stderr or res.stdout).strip()
        if 'HTTP 409' in msg:
            msg += ('\nНа folio есть версия новее page.json: посмотреть `folio info '
                    f'{page.meta.get("folio")}`, слить правки и обновить "version" в page.json.')
        raise PublishError(msg)
    line = next((l for l in reversed(res.stdout.splitlines()) if l.startswith('{')), None)
    if line is None:
        raise PublishError(f'folio не вернул JSON: {res.stdout.strip()}')
    info = json.loads(line)
    page.meta['folio'], page.meta['version'] = info['id'], info['version']
    (page.dir / 'page.json').write_text(json.dumps(page.meta, ensure_ascii=False, indent=2) + '\n',
                                        encoding='utf-8')
    return info
