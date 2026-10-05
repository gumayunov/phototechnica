"""Публикация собранной страницы на folio через CLI скилла fc-folio."""
import json
import os
import subprocess
from pathlib import Path

from .build import ROOT, Page, build_page, unpublished_links
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
    pending = unpublished_links(index.read_text(encoding='utf-8'))
    if pending:
        raise PublishError(f'страница ссылается на неопубликованные страницы, сначала опубликуй: '
                           f'{", ".join(pending)}')
    page = Page(name, root)
    if page.meta.get('folio'):
        cmd = [folio_bin, 'update', page.meta['folio'], str(index.parent)]
        if page.meta.get('version'):
            cmd += ['--base', str(page.meta['version'])]
    else:
        cmd = [folio_bin, 'publish', str(index.parent), '--title', page.meta['title']]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
    except OSError as e:
        raise PublishError(f'не удалось запустить folio CLI {folio_bin}: {e}. '
                           'Путь задаётся переменной PT_FOLIO.') from e
    fid = page.meta.get('folio')
    if res.returncode != 0:
        msg = '\n'.join(s.strip() for s in (res.stderr, res.stdout) if s.strip())
        if 'HTTP 409' in msg:
            msg += ('\nНа folio есть версия новее page.json: ' + (f'посмотреть `folio info {fid}`, ' if fid else '')
                    + 'слить правки и обновить "version" в page.json.')
        raise PublishError(msg)
    line = next((l for l in reversed(res.stdout.splitlines()) if l.startswith('{')), None)
    if line is None:
        raise PublishError(f'folio не вернул JSON: {res.stdout.strip()}')
    try:
        info = json.loads(line)
        new_id, new_version = info['id'], info['version']
    except (ValueError, KeyError, TypeError) as e:
        raise PublishError('Загрузка могла дойти до folio, но ответ не разобран '
                           f'({type(e).__name__}: {e}). Ответ folio:\n{res.stdout.strip()}\n'
                           + (f'Проверьте `folio info {fid}` и ' if fid else 'Проверьте folio и ')
                           + f'впишите "version" в pages/{name}/page.json вручную.') from e
    page.meta['folio'], page.meta['version'] = new_id, new_version
    (page.dir / 'page.json').write_text(json.dumps(page.meta, ensure_ascii=False, indent=2) + '\n',
                                        encoding='utf-8')
    return info
