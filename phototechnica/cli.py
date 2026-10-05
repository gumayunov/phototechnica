"""Команды ./pt."""
import argparse
import sys

from .build import ROOT, BuildError, build_page, list_pages
from .check import check_page, errors
from .folio import PublishError, publish
from .read import outline, text
from .scaffold import new_page


def _check(names):
    ok = True
    for name in names:
        issues = check_page(name, ROOT)
        for issue in issues:
            print(issue, file=sys.stderr)
        ok = ok and not errors(issues)
    return ok


def main(argv):
    ap = argparse.ArgumentParser(prog='pt', description='Сборка, проверка и публикация страниц phototechnica')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for cmd, helptext in [('build', 'проверить и собрать в dist/'), ('check', 'только проверить')]:
        p = sub.add_parser(cmd, help=helptext)
        p.add_argument('page', nargs='?', help='страница; без аргумента — все')
    p = sub.add_parser('outline', help='структура страницы: разделы, заголовки, data-folio-id, объём')
    p.add_argument('page')
    p = sub.add_parser('text', help='чистый текст страницы или раздела')
    p.add_argument('page')
    p.add_argument('section', nargs='?', help='раздел: 06, 06-focus или focus')
    p = sub.add_parser('publish', help='проверить, собрать и выложить новую версию на folio')
    p.add_argument('page')
    p = sub.add_parser('new', help='заготовка новой страницы')
    p.add_argument('page')
    p.add_argument('--title', required=True)
    args = ap.parse_args(argv)

    try:
        if args.cmd in ('build', 'check'):
            names = [args.page] if args.page else list_pages(ROOT)
            if not _check(names):
                return 1
            if args.cmd == 'build':
                for name in names:
                    print(build_page(name, ROOT).relative_to(ROOT))
        elif args.cmd == 'outline':
            print(outline(args.page, ROOT))
        elif args.cmd == 'text':
            print(text(args.page, args.section, ROOT))
        elif args.cmd == 'publish':
            info = publish(args.page, ROOT)
            print(f'версия {info["version"]}: {info["url"]}')
        elif args.cmd == 'new':
            print(new_page(args.page, args.title, ROOT).relative_to(ROOT))
    except (BuildError, PublishError) as e:
        print(f'ошибка: {e}', file=sys.stderr)
        return 1
    return 0
