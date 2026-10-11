from pathlib import Path
import json, re, unicodedata
from urllib.parse import quote
from hero_identity import hero_key

ROSTER=Path('roster/index.html')
LIVE=Path('data/live-meta.json')
SCORE=Path('data/meta-score.json')
CATALOG=Path('data/hero-catalog.json')

for p in [ROSTER,LIVE,SCORE,CATALOG]:
    if not p.exists():
        raise RuntimeError(f'Missing Roster product-card dependency: {p}')

live=json.loads(LIVE.read_text(encoding='utf-8'))
score=json.loads(SCORE.read_text(encoding='utf-8'))
catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
heroes=live.get('heroes',[])
scores=score.get('heroes',[])
editorial_rows=catalog.get('heroes',[])
if len(heroes)!=133 or len(scores)!=133:
    raise RuntimeError(f'Roster product cards require 133 live/score rows; got live={len(heroes)} score={len(scores)}')
if len(editorial_rows)!=34:
    raise RuntimeError(f'Expected 34 editorial heroes, got {len(editorial_rows)}')

score_by={hero_key(r['name']):r for r in scores if r.get('name')}
editorial={hero_key(r['name']) for r in editorial_rows if r.get('name')}

def slug(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')

rows=[]
for h in heroes:
    name=h.get('name')
    if not name: continue
    s=score_by.get(hero_key(name))
    if not s:
        raise RuntimeError(f'Meta Score missing for {name}')
    rows.append({
        'name':name,
        'slug':slug(name),
        'wr':h.get('wr'),
        'ban':h.get('ban'),
        'pick':h.get('pick'),
        'editorial':hero_key(name) in editorial,
        'score':s.get('score'),
        'rank':s.get('rank'),
        'label':s.get('label') or 'Señal estadística'
    })

if len(rows)!=133:
    raise RuntimeError(f'Built {len(rows)} Roster product rows, expected 133')
if sum(1 for r in rows if r['editorial'])!=34:
    raise RuntimeError('Roster product rows did not resolve exactly 34 editorial heroes')

DATA=json.dumps(rows,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
page=ROSTER.read_text(encoding='utf-8')

if 'id="roster-product-cards-style"' in page:
    print('Roster product cards already enhanced')
    raise SystemExit(0)

CSS='''<style id="roster-product-cards-style">
.toolbar{grid-template-columns:minmax(0,1fr) 220px!important}.grid{align-items:stretch}.roster-card{display:flex;flex-direction:column;min-width:0;padding:0!important;overflow:hidden}.roster-card:hover{transform:translateY(-2px);border-color:#46678f!important}.roster-card-main{display:block;padding:16px 16px 12px;min-height:0}.roster-card-main:focus-visible{outline:2px solid #58e5ff;outline-offset:-3px}.roster-card .top{align-items:flex-start}.roster-card .name{line-height:1.08}.roster-card-badges{display:flex;align-items:center;gap:6px;flex-wrap:wrap;justify-content:flex-end}.roster-card-rank{font-size:9px;font-weight:900;color:#9b8aff;border:1px solid #6a5a9a66;border-radius:999px;padding:5px 7px;white-space:nowrap}.roster-card-coverage{font-size:8px;font-weight:900;letter-spacing:.06em;color:#6f829f;border:1px solid #263a56;border-radius:999px;padding:5px 7px;white-space:nowrap}.roster-card-coverage.editorial{color:#ffd36c;border-color:#80653166}.roster-card-score{display:flex;align-items:end;justify-content:space-between;gap:10px;margin-top:14px;padding:11px 12px;border:1px solid #293b57;border-radius:13px;background:linear-gradient(135deg,#0a1423,#151329)}.roster-card-score strong{font-size:28px;line-height:1;color:#cab7ff;letter-spacing:-.04em}.roster-card-score span{font-size:8px;color:#7f91ad;font-weight:900;letter-spacing:.08em;text-align:right}.roster-card .stats{margin-top:9px}.roster-card-actions{display:grid;grid-template-columns:1fr 1fr;gap:7px;padding:0 16px 16px;margin-top:auto}.roster-card-actions a,.roster-card-actions button{display:flex;align-items:center;justify-content:center;min-height:36px;border:1px solid #2b405e;border-radius:10px;background:#0b1524;color:#cbd9ec;text-decoration:none;font:850 10px/1 system-ui;cursor:pointer}.roster-card-actions a:hover,.roster-card-actions button:hover,.roster-card-actions a:focus-visible,.roster-card-actions button:focus-visible{outline:none;border-color:#54e3ff;background:#102035}.roster-card-actions .compare{color:#bca8ff}.roster-card-actions .watch.active{background:#52e3ff;color:#07101b;border-color:#52e3ff}.roster-card-actions .open{grid-column:span 2;color:#63e7ff}.roster-sort-note{margin:-9px 0 16px;color:#7286a5;font-size:10px;line-height:1.5}.roster-sort-note b{color:#a998ff}@media(max-width:580px){.toolbar{grid-template-columns:1fr!important}.roster-card-main{padding:15px}.roster-card-actions{padding:0 15px 15px}}
</style>'''

# Add Meta Score as the first/default sort option.
select_pattern=r'<select id="sort" aria-label="Ordenar">.*?</select>'
select_html='<select id="sort" aria-label="Ordenar"><option value="score">Mayor Meta Score</option><option value="wr">Mayor win rate</option><option value="ban">Mayor ban rate</option><option value="pick">Mayor pick rate</option><option value="name">Nombre A-Z</option></select>'
page,new_count=re.subn(select_pattern,select_html,page,count=1,flags=re.S)
if new_count!=1:
    raise RuntimeError('Could not replace Roster sort selector')

note='<div id="rosterSortNote" class="roster-sort-note"><b>Meta Score</b> es una señal estadística compuesta, no un tier. El #rank mostrado en cada tarjeta siempre corresponde a Meta Score aunque ordenes por otra métrica.</div>'
marker='<div id="grid" class="grid"></div>'
if marker not in page:
    raise RuntimeError('Roster grid marker missing')
page=page.replace(marker,note+marker,1)

# Replace only the generator's original roster runtime. Later scripts can still append their own scripts safely.
start=page.find('<script>const HEROES=')
if start==-1:
    raise RuntimeError('Original Roster runtime not found')
end=page.find('</script>',start)
if end==-1:
    raise RuntimeError('Original Roster runtime closing tag not found')
end+=len('</script>')

JS=f'''<script id="roster-product-cards-script">const HEROES={DATA};const grid=document.getElementById('grid'),q=document.getElementById('q'),sort=document.getElementById('sort'),empty=document.getElementById('empty');const WATCH_KEY='mf_watchlist_v1';function p(v){{return Number.isFinite(v)?v.toFixed(2)+'%':'—'}}function getWatch(){{try{{const v=JSON.parse(localStorage.getItem(WATCH_KEY)||'[]');return Array.isArray(v)?v:[]}}catch{{return []}}}}function setWatch(v){{localStorage.setItem(WATCH_KEY,JSON.stringify([...new Set(v)]))}}function isWatched(n){{return getWatch().includes(n)}}function card(h){{const watched=isWatched(h.name);return `<article class="card roster-card" data-hero="${{h.name}}" data-meta-rank="${{h.rank}}"><a class="roster-card-main" href="../stats/heroes/${{h.slug}}/"><div class="top"><span class="name">${{h.name}}</span><span class="roster-card-badges"><span class="roster-card-rank">#${{h.rank}} META</span><span class="roster-card-coverage ${{h.editorial?'editorial':''}}">${{h.editorial?'EDITORIAL + LIVE':'LIVE'}}</span></span></div><div class="roster-card-score"><strong>${{Number.isFinite(h.score)?h.score.toFixed(1):'—'}}</strong><span>META SCORE<br>${{h.label}}</span></div><div class="stats"><div class="s"><b>${{p(h.wr)}}</b><span>WIN RATE</span></div><div class="s"><b>${{p(h.ban)}}</b><span>BAN</span></div><div class="s"><b>${{p(h.pick)}}</b><span>PICK</span></div></div></a><div class="roster-card-actions"><a class="compare" href="../compare/?a=${{encodeURIComponent(h.name)}}">⚔ Comparar</a><button class="watch ${{watched?'active':''}}" type="button" data-roster-watch="${{h.name}}" aria-pressed="${{watched?'true':'false'}}">${{watched?'★ Siguiendo':'☆ Seguir'}}</button><a class="open" href="../stats/heroes/${{h.slug}}/">Abrir ficha →</a></div></article>`}}function render(){{let rows=HEROES.filter(h=>h.name.toLowerCase().includes(q.value.trim().toLowerCase()));const key=sort.value;rows.sort((a,b)=>key==='name'?a.name.localeCompare(b.name):(Number(b[key]??-1)-Number(a[key]??-1))||a.name.localeCompare(b.name));grid.innerHTML=rows.map(card).join('');empty.style.display=rows.length?'none':'block'}}q.addEventListener('input',render);sort.addEventListener('change',render);grid.addEventListener('click',e=>{{const b=e.target.closest('[data-roster-watch]');if(!b)return;const name=b.dataset.rosterWatch;const v=getWatch();setWatch(v.includes(name)?v.filter(x=>x!==name):[...v,name]);render()}});window.addEventListener('storage',render);sort.value='score';render();</script>'''
page=page[:start]+JS+page[end:]
page=page.replace('</head>',CSS+'</head>',1)
ROSTER.write_text(page,encoding='utf-8')
print(f'Enhanced Live Roster product cards: heroes={len(rows)}; editorial={sum(1 for r in rows if r["editorial"])}; default_sort=score')
