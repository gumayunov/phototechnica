import json,re,html
cr=json.load(open('credits.json'))
fix={'fir0002':'fir0002 (flagstaffotos)','Kevin McCoy':'Kevin McCoy','Daniel Schwen':'Daniel Schwen','Kübelbeck':'Armin Kübelbeck','Hutton':'Andrew Hutton','HuttyMcphoo':'Andrew Hutton'}
def artist(a):
    for k,v in fix.items():
        if k in a: return v
    return a.strip()
def span(f):
    c=cr[f]; return f'<span class="cr">Фото: <a href="{html.escape(c["page"])}" target="_blank" rel="noopener">{html.escape(artist(c["artist"]))}</a>, {html.escape(c["license"])}, Wikimedia Commons</span>'
t=open('template.html').read()
t=re.sub(r'\{\{cr:([^}]+)\}\}',lambda m:span(m.group(1)),t)
seen={};items=[]
for f,c in cr.items():
    if c['page'] in seen: continue
    seen[c['page']]=1
    items.append(f'    <li><a href="{html.escape(c["page"])}" target="_blank" rel="noopener">{html.escape(c["title"])}</a> — {html.escape(artist(c["artist"]))}, {html.escape(c["license"])}</li>')
t=t.replace('{{CREDITS}}','\n'.join(items))
open('photo-basics/index.html','w').write(t)
