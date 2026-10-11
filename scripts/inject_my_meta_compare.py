from pathlib import Path

p=Path('my-meta/index.html')
if not p.exists():
    raise RuntimeError('my-meta/index.html missing')
html=p.read_text(encoding='utf-8')
if 'id="myMetaCompare"' in html:
    print('My Meta compare panel already injected')
    raise SystemExit

css='''<style id="my-meta-compare-style">.mmc-controls{display:grid;grid-template-columns:1fr auto 1fr auto;gap:8px;align-items:center;margin-top:12px}.mmc-controls select{width:100%;background:#0a111e;color:#eef5ff;border:1px solid #2b3f5d;border-radius:12px;padding:10px}.mmc-vs{font-weight:950;color:#9f87ff}.mmc-note{margin-top:10px;color:#7f90aa;font-size:10px}@media(max-width:680px){.mmc-controls{grid-template-columns:1fr}.mmc-vs{text-align:center}}</style>'''
section='''<article id="myMetaCompare" class="panel full"><small>HERO COMPARE · WATCHLIST</small><h2>Compara dos de tus héroes</h2><div id="myMetaCompareBody"><div class="empty">Cargando tu Watchlist…</div></div><div class="mmc-note">La comparación usa stats live y Meta Score. No convierte diferencias estadísticas en una recomendación automática de pick.</div></article>'''
js=r'''<script id="my-meta-compare-script">(()=>{const KEY='mf_watchlist_v1',box=document.getElementById('myMetaCompareBody');if(!box)return;let names=[];try{names=JSON.parse(localStorage.getItem(KEY)||'[]')}catch{}names=Array.isArray(names)?[...new Set(names.filter(Boolean))]:[];if(names.length<2){box.innerHTML='<div class="empty">Sigue al menos 2 héroes para compararlos aquí. <a href="../roster/">Abrir Live Roster →</a></div>';return}const opts=names.map(n=>`<option value="${n.replace(/&/g,'&amp;').replace(/"/g,'&quot;')}">${n}</option>`).join('');box.innerHTML=`<div class="mmc-controls"><select id="mmcA" aria-label="Primer héroe">${opts}</select><span class="mmc-vs">VS</span><select id="mmcB" aria-label="Segundo héroe">${opts}</select><button id="mmcGo" class="btn primary" type="button">Comparar</button></div>`;const a=document.getElementById('mmcA'),b=document.getElementById('mmcB');b.selectedIndex=1;document.getElementById('mmcGo').onclick=()=>{const u=new URL('../compare/',location.href);u.searchParams.set('a',a.value);u.searchParams.set('b',b.value);location.href=u.toString()}})();</script>'''
html=html.replace('</head>',css+'</head>',1)
marker='</section></main>'
if marker not in html:
    raise RuntimeError('My Meta closing marker missing')
html=html.replace(marker,section+'</section></main>',1)
html=html.replace('</body>',js+'</body>',1)
p.write_text(html,encoding='utf-8')
print('Injected My Meta Watchlist compare panel')
