"""Скачать фото с Wikimedia Commons в pages/<страница>/img и дописать атрибуцию в credits.json.

    python3 tools/dl.py <страница> <ширина> "File name.jpg" ["Другой файл.jpg" …]

Имя в img/ строится из названия на Commons: латиница в нижнем регистре и дефисы.
Файл можно переименовать, поменяв и ключ в credits.json. Поле author копирует Artist
с Commons — проверить его и при необходимости сократить вручную.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = 'https://commons.wikimedia.org/w/api.php'
UA = {'User-Agent': 'phototechnica/1.0 (https://github.com/gumayunov/phototechnica)'}


def local_name(title):
    stem, ext = title.rsplit('.', 1) if '.' in title else (title, 'jpg')
    return re.sub(r'[^a-z0-9]+', '-', stem.lower()).strip('-') + '.' + ext.lower()


def fetch(url, tries=4):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:  # 429 и сетевые сбои: подождать и повторить
            if k == tries - 1:
                raise
            print(f'повтор через {5 * (k + 1)} с: {e}', file=sys.stderr)
            time.sleep(5 * (k + 1))


def info(title, width):
    q = urllib.parse.urlencode({
        'action': 'query', 'titles': 'File:' + title, 'prop': 'imageinfo', 'format': 'json',
        'iiprop': 'url|extmetadata', 'iiurlwidth': width,
        'iiextmetadatafilter': 'LicenseShortName|Artist'})
    pages = json.loads(fetch(f'{API}?{q}'))['query']['pages']
    page = next(iter(pages.values()))
    if 'imageinfo' not in page:
        raise SystemExit(f'нет файла на Commons: {title}')
    return page['imageinfo'][0]


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    page, width, titles = argv[0], argv[1], argv[2:]
    page_dir = ROOT / 'pages' / page
    credits_path = page_dir / 'credits.json'
    credits = json.loads(credits_path.read_text(encoding='utf-8')) if credits_path.exists() else {}
    (page_dir / 'img').mkdir(parents=True, exist_ok=True)
    for title in titles:
        ii = info(title, width)
        # gif берём оригиналом: миниатюра Commons теряет анимацию
        src = ii['url'] if title.lower().endswith('.gif') else ii.get('thumburl') or ii['url']
        name = local_name(title)
        (page_dir / 'img' / name).write_bytes(fetch(src))
        meta = ii.get('extmetadata', {})
        artist = re.sub(r'<[^>]+>', '', meta.get('Artist', {}).get('value', '')).strip().split('\n')[0]
        credits[name] = {'title': title, 'page': ii['descriptionurl'],
                         'license': meta.get('LicenseShortName', {}).get('value', ''),
                         'artist': artist, 'author': artist}
        credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(f'img/{name} — {artist}, {credits[name]["license"]}')
        time.sleep(1)


if __name__ == '__main__':
    main(sys.argv[1:])
