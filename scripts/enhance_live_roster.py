from pathlib import Path
import json, html, datetime

LIVE=Path('data/live-meta.json')
ROSTER=Path('roster/index.html')
if not LIVE.exists() or not ROSTER.exists():
    raise RuntimeError('Live meta and roster are required')

meta=json.loads(LIVE.read_text(encoding='utf-8'))
heroes=[h for h in meta.get('heroes',[]) if h.get('name')]
if len(heroes)!=133:
    raise RuntimeError(f'Expected 133 heroes, got {len(heroes)}')
if meta.get('parser_version')!=2 or meta.get('rate_unit')!='percentage_points':
    raise RuntimeError('Live leaders require parser v2 percentage-point data')

def valid(v): return isinstance(v,(int,float)) and not isinstance(v,bool)
def top(key,n=5):
    return sorted([h for h in heroes if valid(h.get(key))],key=lambda h:(-h[key],h['name']))[:n]
def pct(v): return f'{v:.2f}%'
def slug(name):
    import re,unicodedata
    s=''.join(c for c in unicodedata.normalize('NFD',name.lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')
def pretty_date(value):
    try:
        d=datetime.datetime.fromisoformat(str(value).replace('Z','+00:00'))
        months=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
        return f'{d.day} {months[d.month-1]} {d.year}'
    except Exception:
        return str(value or 'fecha no disponible')[:10]

measured=pretty_date(meta.get('source_updated'))

def board(title,key,help_text):
    rows=''.join(
        f'<a class="ll-row" data-leader-rank="{i}" href="../stats/heroes/{slug(h["name"])}/"><span class="ll-rank">#{i}</span><span class="ll-name">{html.escape(h["name"])}</span><strong>{pct(h[key])}</strong></a>'
        for i,h in enumerate(top(key),1)
    )
    return f'<article class="ll-board" data-leader-key="{key}"><div class="ll-head"><span>{title}</span><small>{help_text} · puntos porcentuales</small></div>{rows}</article>'

SECTION=f'''<section id="liveLeaders" class="live-leaders" data-rate-unit="percentage_points" aria-labelledby="liveLeadersTitle"><div class="ll-title"><div><span class="ll-kicker">SNAPSHOT LEADERS · {html.escape(measured)}</span><h2 id="liveLeadersTitle">Quién lidera los números</h2></div><p>Rankings directos del snapshot medido por la fuente. WR, ban y pick se expresan en puntos porcentuales. Un valor alto no equivale por sí solo a “mejor héroe”: contexto, popularidad, rango y composición siguen importando.</p></div><div class="ll-grid">{board('Win rate','wr','Top 5 por WR')}{board('Ban rate','ban','Top 5 por ban')}{board('Pick rate','pick','Top 5 por pick')}</div></section>'''
CSS='''<style id="live-leaders-style">.live-leaders{margin:20px 0;padding:20px;border:1px solid #263650;border-radius:22px;background:linear-gradient(145deg,#0a1321,#0d101d)}.ll-title{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:14px}.ll-title h2{font-size:26px;margin:4px 0 0;letter-spacing:-.035em}.ll-title p{max-width:560px;margin:0;font-size:12px}.ll-kicker{font-size:10px;font-weight:900;letter-spacing:.12em;color:#55e9ff}.ll-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.ll-board{border:1px solid #21314a;border-radius:16px;background:#08111d;overflow:hidden}.ll-head{padding:12px;border-bottom:1px solid #1b2a42}.ll-head span{display:block;font-weight:900}.ll-head small{display:block;color:#71839e;margin-top:3px}.ll-row{display:grid;grid-template-columns:30px 1fr auto;gap:8px;align-items:center;padding:10px 12px;border-top:1px solid #132137}.ll-row:first-of-type{border-top:0}.ll-row:hover{background:#0c192a}.ll-rank{font-size:10px;color:#687b98;font-weight:900}.ll-name{font-size:13px;font-weight:800;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ll-row strong{font-size:12px;color:#cfe9ff}@media(max-width:820px){.ll-grid{grid-template-columns:1fr}.ll-title{align-items:flex-start;flex-direction:column}.ll-title p{max-width:none}}</style>'''

page=ROSTER.read_text(encoding='utf-8')
if 'id="liveLeaders"' not in page:
    if '</head>' not in page:
        raise RuntimeError('Roster head marker missing')
    page=page.replace('</head>',CSS+'</head>',1)
    marker='<div class="toolbar">'
    if marker not in page:
        raise RuntimeError('Roster toolbar marker missing')
    page=page.replace(marker,SECTION+marker,1)
    ROSTER.write_text(page,encoding='utf-8')
print('Enhanced Live Roster with auditable WR, ban and pick leaders in percentage points')
