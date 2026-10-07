from pathlib import Path
import json, html, re, unicodedata

LIVE=Path('data/live-meta.json')
PREV=Path('data/previous-meta.json')
OUT=Path('data/meta-score.json')
ROSTER=Path('roster/index.html')
TRENDS=Path('trends/index.html')
MYMETA=Path('my-meta/index.html')

if not LIVE.exists():
    raise RuntimeError('live-meta.json is required for Meta Score')

cur=json.loads(LIVE.read_text(encoding='utf-8'))
prev=json.loads(PREV.read_text(encoding='utf-8')) if PREV.exists() else {}
heroes=[h for h in cur.get('heroes',[]) if h.get('name')]
if len(heroes)<100:
    raise RuntimeError(f'Meta Score requires >=100 heroes, got {len(heroes)}')
prev_by={h.get('name'):h for h in prev.get('heroes',[]) if h.get('name')}

def finite(v): return isinstance(v,(int,float)) and not isinstance(v,bool)
def slug(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')

def percentiles(values_by_name):
    rows=sorted((v,n) for n,v in values_by_name.items() if finite(v))
    if not rows:return {}
    if len(rows)==1:return {rows[0][1]:50.0}
    out={}
    for i,(v,n) in enumerate(rows):out[n]=100.0*i/(len(rows)-1)
    return out

wr={h['name']:h.get('wr') for h in heroes}
ban={h['name']:h.get('ban') for h in heroes}
pick={h['name']:h.get('pick') for h in heroes}
momentum={}
for h in heroes:
    p=prev_by.get(h['name'],{})
    dwr=(h.get('wr')-p.get('wr')) if finite(h.get('wr')) and finite(p.get('wr')) else 0.0
    dp=(h.get('pick')-p.get('pick')) if finite(h.get('pick')) and finite(p.get('pick')) else 0.0
    db=(h.get('ban')-p.get('ban')) if finite(h.get('ban')) and finite(p.get('ban')) else 0.0
    momentum[h['name']]=0.60*dwr+0.25*dp+0.15*db

pwr,pban,ppick,pmom=map(percentiles,(wr,ban,pick,momentum))
rows=[]
for h in heroes:
    n=h['name']
    score=0.45*pwr.get(n,50)+0.20*ppick.get(n,50)+0.20*pban.get(n,50)+0.15*pmom.get(n,50)
    score=round(score,1)
    label='Señal muy alta' if score>=80 else 'Señal alta' if score>=65 else 'Señal media' if score>=45 else 'Señal baja'
    rows.append({'name':n,'score':score,'label':label,'wr_pct':round(pwr.get(n,50),1),'pick_pct':round(ppick.get(n,50),1),'ban_pct':round(pban.get(n,50),1),'momentum_pct':round(pmom.get(n,50),1),'momentum_raw':round(momentum.get(n,0),3)})
rows.sort(key=lambda x:(-x['score'],x['name']))
for i,r in enumerate(rows,1):r['rank']=i
OUT.write_text(json.dumps({'version':1,'patch':cur.get('patch'),'formula':'45% WR percentile + 20% pick percentile + 20% ban percentile + 15% momentum percentile','momentum_formula':'60% delta WR + 25% delta pick + 15% delta ban','heroes':rows},ensure_ascii=False,indent=2),encoding='utf-8')
by={r['name']:r for r in rows}

def top_cards(n=10):
    return ''.join(f'<a class="ms-card" href="../stats/heroes/{slug(r["name"])}/"><span class="ms-rank">#{r["rank"]}</span><span class="ms-name">{html.escape(r["name"])}</span><strong>{r["score"]:.1f}</strong><small>{r["label"]}</small></a>' for r in rows[:n])

CSS='''<style id="meta-score-style">.meta-score-panel{margin:18px 0;padding:20px;border:1px solid #334764;border-radius:22px;background:linear-gradient(145deg,#0a1322,#141225)}.ms-head{display:flex;justify-content:space-between;gap:18px;align-items:flex-end}.ms-head h2{margin:4px 0 0}.ms-head p{max-width:650px;margin:0;color:#8fa0bb;font-size:12px;line-height:1.55}.ms-kicker{font-size:10px;font-weight:900;letter-spacing:.13em;color:#b89cff}.ms-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:14px}.ms-card{display:grid;grid-template-columns:auto 1fr auto;gap:7px;align-items:center;border:1px solid #263954;border-radius:13px;padding:10px;background:#0a1422}.ms-card:hover{border-color:#6f5fa0}.ms-rank{font-size:9px;color:#6f819d;font-weight:900}.ms-name{font-size:12px;font-weight:850;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ms-card strong{color:#c4acff;font-size:13px}.ms-card small{grid-column:2/-1;color:#7689a7;font-size:9px}.ms-formula{margin-top:12px;padding-top:11px;border-top:1px solid #22334c;color:#7588a6;font-size:10px;line-height:1.55}.ms-watch{display:grid;gap:8px;margin-top:12px}.ms-watch-row{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:9px;align-items:center;padding:10px 11px;border:1px solid #263954;border-radius:12px;background:#0a1422}.ms-watch-row b{font-size:12px}.ms-watch-row span{font-size:11px;color:#8ea0bc}.ms-watch-row strong{font-size:13px;color:#c4acff}@media(max-width:900px){.ms-grid{grid-template-columns:1fr 1fr}.ms-head{align-items:flex-start;flex-direction:column}}@media(max-width:560px){.ms-grid{grid-template-columns:1fr}.ms-watch-row{grid-template-columns:1fr auto}.ms-watch-row span{grid-column:1/-1}}</style>'''
FORMULA='<div class="ms-formula"><b>Meta Score estadístico, no tier:</b> 45% percentil WR + 20% percentil pick + 20% percentil ban + 15% percentil momentum. Momentum = 60% ΔWR + 25% Δpick + 15% Δban. No representa probabilidad de victoria.</div>'

# Live Roster: top 10 Meta Score.
if not ROSTER.exists():raise RuntimeError('roster/index.html missing')
page=ROSTER.read_text(encoding='utf-8')
if 'id="metaScorePanel"' not in page:
    section=f'<section id="metaScorePanel" class="meta-score-panel"><div class="ms-head"><div><span class="ms-kicker">META SCORE · LIVE</span><h2>Señal estadística compuesta</h2></div><p>Resume rendimiento, presencia y movimiento reciente en una escala 0–100. Sirve para detectar señal estadística, no para reemplazar el análisis de draft ni el tier editorial.</p></div><div class="ms-grid">{top_cards()}</div>{FORMULA}</section>'
    page=page.replace('</head>',CSS+'</head>',1)
    marker='<div class="toolbar">'
    if marker not in page:raise RuntimeError('Roster toolbar missing for Meta Score')
    page=page.replace(marker,section+marker,1)
    ROSTER.write_text(page,encoding='utf-8')

# Trends: add a compact top-score section. Links are live-stat links by design.
if not TRENDS.exists():raise RuntimeError('trends/index.html missing')
page=TRENDS.read_text(encoding='utf-8')
if 'id="trendsMetaScore"' not in page:
    section=f'<section id="trendsMetaScore" class="meta-score-panel"><div class="ms-head"><div><span class="ms-kicker">META SCORE</span><h2>Mayor señal estadística ahora</h2></div><p>Ranking transversal de los 133 héroes. Es independiente del modo Editorial y no asigna tiers.</p></div><div class="ms-grid">{top_cards(10)}</div>{FORMULA}</section>'
    page=page.replace('</head>',CSS+'</head>',1)
    marker='<section class="all">'
    if marker not in page:raise RuntimeError('Trends all-section marker missing')
    page=page.replace(marker,section+marker,1)
    TRENDS.write_text(page,encoding='utf-8')

# My Meta: compute score rows dynamically only for watched heroes.
if not MYMETA.exists():raise RuntimeError('my-meta/index.html missing')
page=MYMETA.read_text(encoding='utf-8')
if 'id="myMetaScore"' not in page:
    score_json=json.dumps(by,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    section=f'<article id="myMetaScore" class="panel full"><small>META SCORE · WATCHLIST</small><h2>Señal estadística de tus héroes</h2><div id="myMetaScoreRows" class="ms-watch"><div class="empty">Cargando Meta Score…</div></div>{FORMULA}</article>'
    js=f'''<script id="my-meta-score-script">(()=>{{const SCORES={score_json};const KEY='mf_watchlist_v1';let names=[];try{{names=JSON.parse(localStorage.getItem(KEY)||'[]')}}catch{{}}const box=document.getElementById('myMetaScoreRows');if(!box)return;const rows=(Array.isArray(names)?names:[]).map(n=>SCORES[n]).filter(Boolean).sort((a,b)=>b.score-a.score);box.innerHTML=rows.length?rows.map(r=>`<a class="ms-watch-row" href="../stats/heroes/${{r.name.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}}/"><b>${{r.name}}</b><span>#${{r.rank}} del roster · ${{r.label}}</span><strong>${{r.score.toFixed(1)}}</strong></a>`).join(''):'<div class="empty">Sigue héroes para comparar su Meta Score.</div>'}})();</script>'''
    page=page.replace('</head>',CSS+'</head>',1)
    marker='</section></main>'
    if marker not in page:raise RuntimeError('My Meta closing section marker missing')
    page=page.replace(marker,section+'</section></main>',1)
    page=page.replace('</body>',js+'</body>',1)
    MYMETA.write_text(page,encoding='utf-8')

print(f'Injected Meta Score for {len(rows)} heroes; top={rows[0]["name"]} {rows[0]["score"]}')
