from pathlib import Path
import json

PAGE=Path('explore/index.html')
SCORE=Path('data/meta-score.json')
CATALOG=Path('data/hero-catalog.json')
if not PAGE.exists() or not SCORE.exists() or not CATALOG.exists():
    raise RuntimeError('Meta Explorer tools require explore page, score and catalog')
page=PAGE.read_text(encoding='utf-8')
if 'id="explorerPowerTools"' in page:
    print('Meta Explorer power tools already present')
    raise SystemExit
score=json.loads(SCORE.read_text(encoding='utf-8'))
catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
rows=[{'name':h['name'],'rank':h['rank']} for h in score.get('heroes',[]) if h.get('name')]
if len(rows)!=133: raise RuntimeError(f'Explorer power tools expected 133 score rows, got {len(rows)}')
editorial={h.get('name') for h in catalog.get('heroes',[]) if h.get('name')}
if len(editorial)!=34: raise RuntimeError(f'Explorer power tools expected 34 editorial names, got {len(editorial)}')
data=json.dumps(rows,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
editorial_json=json.dumps(sorted(editorial),ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
css='''<style id="explorer-power-style">.explorer-power{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:12px}.explorer-scope{border:1px solid #2d425e;border-radius:999px;background:#09121f;color:#8fa2bd;padding:8px 11px;font-size:10px;font-weight:900;cursor:pointer}.explorer-scope[aria-pressed="true"]{border-color:#50e4ff;color:#5ceaff;background:#102032}.explorer-count{margin-left:auto;color:#7488a6;font-size:10px;font-weight:850}.explorer-pair{position:sticky;bottom:12px;z-index:60;margin-top:12px;display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:11px 12px;border:1px solid #36506f;border-radius:16px;background:#08121ef2;box-shadow:0 14px 38px #0008;backdrop-filter:blur(12px)}.explorer-pair-slots{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.pair-slot{padding:8px 10px;border:1px dashed #38516f;border-radius:11px;color:#8194b0;font-size:10px}.pair-slot.filled{border-style:solid;color:#eef6ff;background:#101d2e}.pair-actions{display:flex;gap:7px;flex-wrap:wrap}.pair-actions button,.pair-actions a{padding:8px 10px;border:1px solid #35506e;border-radius:10px;background:#0c1828;color:#b5c8df;font-size:10px;font-weight:900;text-decoration:none}.pair-actions a.ready{background:#54e7ff;color:#07111b;border-color:#54e7ff}.pair-actions a[aria-disabled="true"]{opacity:.45;pointer-events:none}.explorer-empty{padding:14px;border:1px dashed #3d5879;border-radius:12px;color:#c7d7ec;font-size:13px}.explorer-scope-note{font-size:12px;color:#92a9c6}.pair-slot.filled:after{content:" ×";color:#62e6ff}.pair-actions button:disabled{opacity:.45;cursor:default}.explorer-selection-note{color:#768ba8;font-size:9px}@media(max-width:700px){.explorer-count{width:100%;margin-left:0}.explorer-pair{grid-template-columns:1fr}.pair-actions{justify-content:flex-start}}</style>'''
markup='''<div id="explorerPowerTools" class="explorer-power" aria-label="Filtros del Meta Explorer"><button class="explorer-scope" data-explorer-scope="all" aria-pressed="true" type="button">Todos · 133</button><button class="explorer-scope" data-explorer-scope="watch" aria-pressed="false" type="button">★ Siguiendo</button><button class="explorer-scope" data-explorer-scope="editorial" aria-pressed="false" type="button">Editorial · 34</button><button class="explorer-scope" data-explorer-scope="top20" aria-pressed="false" type="button">Top 20 Meta</button><span id="explorerVisibleCount" class="explorer-count" role="status" aria-live="polite" aria-atomic="true">133 de 133 héroes</span></div><p id="explorerLocalScope" class="explorer-scope-note" hidden>El filtro Siguiendo utiliza los favoritos guardados en este dispositivo.</p><p id="explorerEmpty" class="explorer-empty" hidden></p>'''
pair='''<div id="explorerPairTray" class="explorer-pair" aria-label="Comparación seleccionada"><div><div class="explorer-pair-slots"><button id="explorerPairA" class="pair-slot" type="button" disabled>A · vacío</button><span>VS</span><button id="explorerPairB" class="pair-slot" type="button" disabled>B · vacío</button></div><div id="explorerSelectionNote" class="explorer-selection-note">Selecciona un punto del mapa y añádelo a la comparación.</div></div><div class="pair-actions"><button id="explorerAddSelected" type="button" disabled>Añadir selección</button><button id="explorerClearPair" type="button">Limpiar</button><a id="explorerComparePair" href="../compare/" aria-disabled="true">Comparar A/B</a></div></div>'''
js=f'''<script id="explorer-power-runtime">(()=>{{
const META={data},EDITORIAL=new Set({editorial_json}),WATCH_KEY='mf_watchlist_v1';
const byName=new Map(META.map(x=>[x.name,x]));
const buttons=[...document.querySelectorAll('[data-explorer-scope]')],count=document.getElementById('explorerVisibleCount'),svg=document.getElementById('metaPlot'),table=document.querySelector('.table-wrap tbody'),search=document.getElementById('exploreSearch'),empty=document.getElementById('explorerEmpty'),add=document.getElementById('explorerAddSelected'),clear=document.getElementById('explorerClearPair'),compare=document.getElementById('explorerComparePair'),slotA=document.getElementById('explorerPairA'),slotB=document.getElementById('explorerPairB'),note=document.getElementById('explorerSelectionNote');
const params=new URLSearchParams(location.search);
let scope=['all','watch','editorial','top20'].includes(params.get('scope'))?params.get('scope'):'all';
let current=byName.has(params.get('hero'))?params.get('hero'):null;
let pair=[...new Set([params.get('a'),params.get('b')].filter(name=>byName.has(name)))].slice(0,2);
const rows=[...table.querySelectorAll('tr[data-key]')];
const namesByKey=new Map(rows.map(tr=>[tr.dataset.key,tr.querySelector('a').textContent.trim()]));
const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
function watch(){{try{{const x=JSON.parse(localStorage.getItem(WATCH_KEY)||'[]');return new Set(Array.isArray(x)?x:[])}}catch{{return new Set()}}}}
function saveView(){{const u=new URL(location.href);if(scope==='all')u.searchParams.delete('scope');else u.searchParams.set('scope',scope);['a','b'].forEach((key,i)=>{{if(pair[i])u.searchParams.set(key,pair[i]);else u.searchParams.delete(key)}});history.replaceState(null,'',u)}}
function syncVisibility(){{
 const followed=watch(),query=normalize(search.value);
 function allowed(name){{const row=byName.get(name);if(!row||!normalize(name).includes(query))return false;if(scope==='watch')return followed.has(name);if(scope==='editorial')return EDITORIAL.has(name);if(scope==='top20')return row.rank<=20;return true}}
 let visible=0;
 for(const c of svg.querySelectorAll('.dot')){{const ok=allowed(namesByKey.get(c.dataset.key)||'');c.style.display=ok?'':'none';c.classList.remove('dim');c.setAttribute('aria-pressed',c.classList.contains('hit')?'true':'false');if(ok)visible++}}
 for(const tr of rows)tr.hidden=!allowed(namesByKey.get(tr.dataset.key));
 count.textContent=visible+' de '+META.length+' héroes';
 empty.hidden=visible!==0;
 empty.textContent=scope==='watch'&&followed.size===0?'Aún no sigues a ningún héroe. Puedes añadirlos desde Roster o desde sus fichas.':'No hay héroes que coincidan. Cambia el filtro o borra la búsqueda.';
 document.getElementById('explorerLocalScope').hidden=scope!=='watch';
 for(const b of buttons)b.setAttribute('aria-pressed',b.dataset.explorerScope===scope?'true':'false');
 document.getElementById('exploreTooltip').hidden=true;
 saveView();syncPair();
}}
function syncPair(){{
 slotA.textContent=pair[0]?'A · '+pair[0]:'A · vacío';slotB.textContent=pair[1]?'B · '+pair[1]:'B · vacío';
 slotA.classList.toggle('filled',!!pair[0]);slotB.classList.toggle('filled',!!pair[1]);
 [slotA,slotB].forEach((slot,i)=>{{slot.disabled=!pair[i];slot.setAttribute('aria-label',pair[i]?'Quitar '+pair[i]+' de la comparación':'Puesto '+(i?'B':'A')+' vacío');slot.title=pair[i]?'Quitar de la comparación':''}});
 const ready=pair.length===2;
 compare.setAttribute('aria-disabled',ready?'false':'true');compare.tabIndex=ready?0:-1;compare.classList.toggle('ready',ready);
 compare.href=ready?`../compare/?a=${{encodeURIComponent(pair[0])}}&b=${{encodeURIComponent(pair[1])}}`:'../compare/';
 const point=current?[...svg.querySelectorAll('.dot')].find(c=>namesByKey.get(c.dataset.key)===current):null;
 const visible=point&&point.style.display!=='none';
 note.textContent=current?`Seleccionado: ${{current}}. ${{pair.includes(current)?'Ya está en A/B.':pair.length>=2?'Quita un héroe para cambiar la pareja.':visible?'Puedes añadirlo.':'No está en el filtro actual.'}}`:'Selecciona un punto del mapa y añádelo a la comparación.';
 add.disabled=!current||!visible||pair.includes(current)||pair.length>=2;
 clear.disabled=pair.length===0;
}}
for(const b of buttons)b.addEventListener('click',()=>{{scope=b.dataset.explorerScope;syncVisibility()}});
svg.addEventListener('mf:explorer-selected',e=>{{current=byName.has(e.detail?.name)?e.detail.name:null;syncPair()}});
add.addEventListener('click',()=>{{if(add.disabled||!current||pair.includes(current)||pair.length>=2)return;pair.push(current);syncPair();saveView()}});
clear.addEventListener('click',()=>{{pair=[];syncPair();saveView()}});
[slotA,slotB].forEach((slot,i)=>slot.addEventListener('click',()=>{{pair.splice(i,1);syncPair();saveView()}}));
compare.addEventListener('click',e=>{{if(pair.length!==2)e.preventDefault()}});
const observer=new MutationObserver(()=>syncVisibility());if(svg)observer.observe(svg,{{childList:true}});
window.addEventListener('storage',e=>{{if(e.key===WATCH_KEY||e.key===null)syncVisibility()}});
syncVisibility();
}})();
</script>'''
if '<div id="plotWrap"' not in page: raise RuntimeError('Explorer plot marker missing')
page=page.replace('<div id="plotWrap"',markup+'<div id="plotWrap"',1)
if '<p class="disclaimer">' not in page: raise RuntimeError('Explorer disclaimer marker missing')
page=page.replace('<p class="disclaimer">',pair+'<p class="disclaimer">',1)
page=page.replace('</head>',css+'</head>',1)
page=page.replace('</body>',js+'</body>',1)
PAGE.write_text(page,encoding='utf-8')
print('Meta Explorer power tools injected: scopes=all/watch/editorial/top20; pair_limit=2; shared_watchlist=true; direct_compare=true')
