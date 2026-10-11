from pathlib import Path
import json, html, re, unicodedata
from meta_score_core import compute_score_rows, FORMULA, MOMENTUM_FORMULA

HISTORY=Path('data/meta-history.json')
OUT=Path('data/meta-score-history.json')
TRENDS=Path('trends/index.html')
MYMETA=Path('my-meta/index.html')

if not HISTORY.exists():
    raise RuntimeError('meta-history.json is required')
raw=json.loads(HISTORY.read_text(encoding='utf-8'))
snaps=raw.get('snapshots',raw if isinstance(raw,list) else [])
if not isinstance(snaps,list) or not snaps:
    raise RuntimeError('Meta history has no snapshots')

def slug(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')

history=[]
previous=[]
for snap in snaps:
    heroes=[h for h in snap.get('heroes',[]) if h.get('name')]
    if len(heroes)<100:
        continue
    rows=compute_score_rows(heroes,previous)
    history.append({
        'updated':snap.get('updated'),
        'patch':snap.get('patch'),
        'fetched_at':snap.get('fetched_at'),
        'heroes':rows,
    })
    previous=heroes

if not history:
    raise RuntimeError('No valid >=100-hero snapshots for Meta Score history')

snapshot_count=len(history)
history_status='active' if snapshot_count>=2 else 'waiting_for_real_change'
OUT.write_text(json.dumps({
    'version':2,
    'formula':FORMULA,
    'momentum_formula':MOMENTUM_FORMULA,
    'percentile_method':'average rank for ties',
    'snapshot_count':snapshot_count,
    'history_status':history_status,
    'history_rule':'new snapshot only when patch or live WR/ban/pick changes semantically',
    'snapshots':history
},ensure_ascii=False,indent=2),encoding='utf-8')

latest=history[-1]
prior=history[-2] if len(history)>=2 else None
latest_by={r['name']:r for r in latest['heroes']}
prior_by={r['name']:r for r in prior['heroes']} if prior else {}
changes=[]
for name,a in latest_by.items():
    b=prior_by.get(name)
    if not b: continue
    changes.append({'name':name,'score':a['score'],'rank':a['rank'],'score_delta':round(a['score']-b['score'],1),'rank_delta':b['rank']-a['rank']})
risers=sorted(changes,key=lambda x:(-x['score_delta'],-x['rank_delta'],x['name']))[:6]
fallers=sorted(changes,key=lambda x:(x['score_delta'],x['rank_delta'],x['name']))[:6]

CSS='''<style id="meta-score-history-style">.msh-panel{margin:18px 0;padding:20px;border:1px solid #334764;border-radius:22px;background:#0a1220}.msh-head{display:flex;justify-content:space-between;gap:16px;align-items:flex-end}.msh-head h2{margin:4px 0 0}.msh-head p{max-width:640px;margin:0;color:#8799b5;font-size:12px}.msh-status{display:inline-flex;margin-top:8px;padding:6px 9px;border:1px solid #3b4560;border-radius:999px;background:#101827;color:#bac8dc;font-size:10px;font-weight:900}.msh-status.wait{color:#ffd36c;border-color:#5b4b25;background:#18150d}.msh-status.active{color:#83e8b7;border-color:#275343;background:#0d1814}.msh-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}.msh-list{display:grid;gap:7px}.msh-row{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:8px;align-items:center;padding:10px;border:1px solid #25364f;border-radius:12px;background:#0c1625;text-decoration:none;color:inherit}.msh-row b{font-size:12px}.msh-row span{font-size:10px;color:#8597b2}.msh-up{color:#83e8b7!important;font-weight:900}.msh-down{color:#ff9d9d!important;font-weight:900}.msh-note{margin-top:11px;color:#71829d;font-size:10px;line-height:1.5}.msh-watch{display:grid;gap:8px;margin-top:12px}@media(max-width:760px){.msh-grid{grid-template-columns:1fr}.msh-head{align-items:flex-start;flex-direction:column}}</style>'''

def rows_html(rows,up=True):
    if not rows:
        return '<div class="empty">Historial insuficiente.</div>'
    return ''.join(f'<a class="msh-row" href="../stats/heroes/{slug(r["name"])}/"><b>{html.escape(r["name"])}</b><span>#{r["rank"]} · {r["score"]:.1f}</span><span class="{"msh-up" if r["score_delta"]>=0 else "msh-down"}">{r["score_delta"]:+.1f} score · {r["rank_delta"]:+d} puestos</span></a>' for r in rows)

if snapshot_count>=2:
    status_text=f'{snapshot_count} snapshots reales · historial activo'
    status_class='active'
else:
    status_text='1 snapshot real · esperando cambio real'
    status_class='wait'
status_html=f'<span class="msh-status {status_class}" data-history-status="{history_status}" data-history-snapshots="{snapshot_count}">{status_text}</span>'

if TRENDS.exists():
    page=TRENDS.read_text(encoding='utf-8')
    if 'id="metaScoreHistory"' not in page:
        if snapshot_count>=2:
            body=f'<div class="msh-grid"><article><h3>📈 Score Risers</h3><div class="msh-list">{rows_html(risers)}</div></article><article><h3>📉 Score Fallers</h3><div class="msh-list">{rows_html(fallers,False)}</div></article></div>'
            note=f'{snapshot_count} snapshots recalculados con la misma fórmula.'
        else:
            body='<div class="empty">Todavía no existe un segundo punto real para calcular movimiento.</div>'
            note='Se añadirá otro snapshot solo cuando cambie de verdad el patch o alguna tasa live WR/ban/pick. Una nueva consulta sin cambios no crea tendencia.'
        section=f'<section id="metaScoreHistory" class="msh-panel"><div class="msh-head"><div><span class="ms-kicker">META SCORE HISTORY</span><h2>Quién gana o pierde señal</h2>{status_html}</div><p>Compara Meta Score recalculado con la misma fórmula entre snapshots reales. No es un cambio de tier ni una probabilidad de victoria.</p></div>{body}<div class="msh-note">{note}</div></section>'
        page=page.replace('</head>',CSS+'</head>',1)
        marker='<section class="all">'
        if marker not in page: raise RuntimeError('Trends marker missing for Meta Score history')
        page=page.replace(marker,section+marker,1)
        TRENDS.write_text(page,encoding='utf-8')

if MYMETA.exists():
    page=MYMETA.read_text(encoding='utf-8')
    if 'id="myMetaScoreHistory"' not in page:
        history_json=json.dumps({'latest':latest_by,'prior':prior_by},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
        section=f'<article id="myMetaScoreHistory" class="panel full" data-history-status="{history_status}" data-history-snapshots="{snapshot_count}"><small>META SCORE HISTORY · WATCHLIST</small><h2>Cómo se mueven tus héroes</h2>{status_html}<div id="myMetaScoreHistoryRows" class="msh-watch"><div class="empty">Cargando historial…</div></div><div class="msh-note">El delta compara los dos últimos snapshots reales. Una simple consulta del mismo dato no crea un punto histórico nuevo.</div></article>'
        js=f'''<script id="my-meta-score-history-script">(()=>{{const H={history_json};const KEY='mf_watchlist_v1';let names=[];try{{names=JSON.parse(localStorage.getItem(KEY)||'[]')}}catch{{}}const box=document.getElementById('myMetaScoreHistoryRows');if(!box)return;if(!H.prior||!Object.keys(H.prior).length){{box.innerHTML='<div class="empty">Aún falta un segundo snapshot real para calcular movimientos.</div>';return}}const rows=(Array.isArray(names)?names:[]).map(n=>{{const a=H.latest[n],b=H.prior[n];return a&&b?{{name:n,score:a.score,rank:a.rank,ds:+(a.score-b.score).toFixed(1),dr:b.rank-a.rank}}:null}}).filter(Boolean).sort((a,b)=>Math.abs(b.ds)-Math.abs(a.ds));box.innerHTML=rows.length?rows.map(r=>`<a class="msh-row" href="../stats/heroes/${{r.name.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}}/"><b>${{r.name}}</b><span>#${{r.rank}} · ${{r.score.toFixed(1)}}</span><span class="${{r.ds>=0?'msh-up':'msh-down'}}">${{r.ds>=0?'+':''}}${{r.ds.toFixed(1)}} score · ${{r.dr>=0?'+':''}}${{r.dr}} puestos</span></a>`).join(''):'<div class="empty">Tus héroes seguidos no tienen comparación histórica disponible.</div>'}})();</script>'''
        page=page.replace('</head>',CSS+'</head>',1)
        marker='</section></main>'
        if marker not in page: raise RuntimeError('My Meta marker missing for Meta Score history')
        page=page.replace(marker,section+'</section></main>',1)
        page=page.replace('</body>',js+'</body>',1)
        MYMETA.write_text(page,encoding='utf-8')

print(f'Built Meta Score history for {snapshot_count} snapshots; status={history_status}; comparisons={len(changes)}')
