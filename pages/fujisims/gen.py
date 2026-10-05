"""Генерируемые части страницы симуляций: карточки, данные вьюера, список фото."""
import html
import json


def bars(n, col):
    return ''.join(f'<i style="background:{col if i < n else "var(--line)"}"></i>' for i in range(5))


def card(s):
    sat = ('<span class="muted">ч/б</span>' if s['s'] == 0
           else f'<span class="bars">{bars(s["s"], "var(--t)")}</span>')
    bad = '<p><b>Не очень:</b> ' + s['bad'] + '</p>' if s['bad'] != '—' else ''
    return f'''<article class="simcard" data-folio-id="card-{s["k"]}">
      <img src="img/mill-{s["k"]}.jpg" alt="{s["name"]} — мельница" loading="lazy">
      <div class="simcard-b">
        <h3>{s["name"]}</h3>
        <p class="film">{s["film"]}</p>
        <p class="quote">{s["manual"]}</p>
        <div class="meters"><span>Контраст</span><span class="bars">{bars(s["c"], "var(--f)")}</span><span>Насыщенность</span>{sat}</div>
        <p><b>Хорошо:</b> {s["good"]}</p>
        {bad}
        <p class="tip">{s["tip"]}</p>
      </div>
    </article>'''


def credit_list(credits):
    items, seen = [], set()
    for _, c in sorted(credits.items()):
        if c['page'] in seen:
            continue
        seen.add(c['page'])
        items.append(f'<li><a href="{html.escape(c["page"])}" target="_blank" rel="noopener">'
                     f'{html.escape(c["title"])}</a> — {html.escape(c["author"])}, {html.escape(c["license"])}</li>')
    return ''.join(items)


def generate(page):
    sims = json.loads((page.dir / 'data' / 'sims.json').read_text(encoding='utf-8'))
    scenes = {k: page.cr(k) for k in page.credits if k.startswith(('mill', 'box', 'sheep'))}
    return {
        'sims-json': json.dumps(sims, ensure_ascii=False),
        'cr-json': json.dumps(scenes, ensure_ascii=False),
        'sim-cards': ''.join(card(s) for s in sims if s['xs']),
        'credit-list': credit_list(page.credits),
    }
