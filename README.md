# phototechnica

Учебные страницы об основах фотографии и исходники, из которых они собираются.

| Страница | Что внутри |
|---|---|
| [Основы фотографии](https://folio.fold-core.ru/a/bernhard/osnovy-fotografii-iso-f-vyderzhka-fokusn-fe0kh3se/) | диафрагма, выдержка, ISO, фокусировка, фокусное расстояние, динамический диапазон; схемы и симуляторы |
| [Симуляции плёнки Fujifilm X-S10](https://folio.fold-core.ru/a/bernhard/simulyatsii-plenki-fujifilm-x-s10-kejiswf8/) | как выглядят симуляции, для каких сцен подходят, рецепты |

Страница собирается в один `index.html` с инлайновыми SVG и JS и папкой `img/`.
Нужен только Python 3.11+, сторонних зависимостей нет.

## Как устроено

```
pt                       CLI: build, check, outline, text, publish, new
phototechnica/           код CLI
shared/                  общая шапка <head> и стили base.css
pages/<страница>/
  page.json              заголовок, адрес и версия на folio
  layout.html            каркас страницы: порядок разделов и скриптов
  sections/NN-имя.html   разделы — HTML-фрагменты
  svg/  js/  css/        схемы, интерактивы, стили страницы
  img/  credits.json     фотографии и их атрибуция
  gen.py, data/          необязательно: генерируемые части страницы
tools/dl.py              скачать фото с Wikimedia Commons с атрибуцией
```

В исходниках вместо повторяющихся кусков стоят метки:

| Метка | Чем заменяется |
|---|---|
| `{{section:06-focus}}` | `sections/06-focus.html` |
| `{{svg:имя}}`, `{{js:имя}}`, `{{css:имя}}` | файл страницы из `svg/`, `js/`, `css/` |
| `{{shared:base.css}}` | файл из `shared/` |
| `{{cr:фото.jpg}}` | подпись «Фото: автор, лицензия, Wikimedia Commons» из `credits.json` |
| `{{credits}}` | список всех фото страницы |
| `{{url:страница}}` | адрес другой страницы на folio |
| `{{title}}` | заголовок из `page.json` |
| `{{gen:имя}}` | значение, которое вернул `gen.py` страницы |

## Команды

```bash
./pt build [страница]          # проверить и собрать в dist/
./pt check [страница]          # только проверить: вложенность тегов, метки, data-folio-id, картинки
./pt outline <страница>        # разделы, заголовки, data-folio-id, число слов и рисунков
./pt text <страница> [раздел]  # чистый текст страницы или раздела (06, 06-focus, focus)
./pt publish <страница>        # собрать и выложить новую версию на folio (только folio.fold-core.ru)
./pt new <slug> --title "…"    # заготовка новой страницы
python3 -m unittest discover -s tests -t .
```

`./pt publish` выкладывает только на folio (folio.fold-core.ru) и требует CLI folio
(скилл fc-folio). Путь к нему берётся из `PT_FOLIO`, по умолчанию
`~/.claude/skills/fc-folio/scripts/folio`.

## Лицензии

- Код (`pt`, `phototechnica/`, `tools/`, `tests/`, а также Python-файлы в `pages/`,
  например `gen.py`) — [MIT](LICENSE).
- Тексты, схемы и интерактивы страниц (`pages/`, `shared/`, кроме фотографий и Python-файлов) —
  [CC BY-SA 4.0](LICENSE-CONTENT.md). Цитаты из сторонних источников (например, из
  руководства FUJIFILM X-S10) приведены со ссылкой на источник и под CC BY-SA не подпадают.
- Фотографии в `pages/*/img/` взяты с Wikimedia Commons и остаются под лицензиями своих
  авторов; автор, лицензия и ссылка на оригинал каждой — в `pages/*/credits.json`.
