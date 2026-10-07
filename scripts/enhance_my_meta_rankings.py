from pathlib import Path

p=Path('my-meta/index.html')
if not p.exists():
    raise RuntimeError('my-meta/index.html not found')
html=p.read_text(encoding='utf-8')
if 'id="myMetaRankings"' in html:
    print('My Meta rankings already injected')
    raise SystemExit

css='''<style id="my-meta-rankings-style">
.rank-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:9px}.rank-card{border:1px solid #24354f;border-radius:14px;padding:12px;background:#0e1727}.rank-card-head{display:flex;justify-content:space-between;gap:10px;align-items:center}.rank-card-head b{font-size:13px}.rank-best{color:#66e5ff;font-size:10px;font-weight:900}.rank-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:10px}.rank-metric{padding:8px;border-radius:10px;background:#09111d;border:1px solid #1e3049}.rank-metric b{display:block;font-size:14px}.rank-metric span{display:block;margin-top:3px;color:#778aa8;font-size:8px;font-weight:900;letter-spacing:.06em}.rank-top10{border-color:#4cc8e866;background:#0b1c2b}.rank-top10 b{color:#6de7ff}.rank-note{margin-top:10px;color:#71819d;font-size:10px;line-height:1.5}@media(max-width:700px){.rank-grid{grid-template-columns:1fr}}
</style>'''
html=html.replace('</head>',css+'</head>',1)

panel='''<article id="myMetaRankings" class="panel full"><small>LIVE RANKINGS</small><h2>Posición en el roster</h2><div id="myMetaRankGrid" class="rank-grid"><div class="empty">Calculando posiciones…</div></div><p class="rank-note">Ranking calculado sobre todos los héroes que tienen esa métrica en el snapshot live. Es una posición estadística, no un tier editorial.</p></article>'''
anchor='<article class="panel full"><small>OVERVIEW</small>'
if anchor not in html:
    raise RuntimeError('Could not locate My Meta overview anchor')
html=html.replace(anchor,panel+anchor,1)

js=r'''<script id="my-meta-rankings-script">
(async()=>{
const box=document.getElementById('myMetaRankGrid');if(!box)return;
const read=(k,f)=>{try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}catch{return f}};
const watch=read('mf_watchlist_v1',[]),profile=read('mf_profile_v1',null);
const names=[...new Set([...(profile?.heroes||[]),...(Array.isArray(watch)?watch:[])])];
if(!names.length){box.innerHTML='<div class="empty">Sigue héroes para ver su posición dentro del roster live.</div>';return}
let meta=null;try{const r=await fetch('../data/live-meta.json',{cache:'no-store'});if(r.ok)meta=await r.json()}catch{}
const heroes=meta?.heroes||[];if(!heroes.length){box.innerHTML='<div class="empty">No hay snapshot live disponible.</div>';return}
const rankMetric=key=>new Map([...heroes].filter(h=>Number.isFinite(h[key])).sort((a,b)=>b[key]-a[key]).map((h,i)=>[h.name,{rank:i+1,total:heroes.filter(x=>Number.isFinite(x[key])).length,value:h[key]}]));
const maps={wr:rankMetric('wr'),ban:rankMetric('ban'),pick:rankMetric('pick')};
const slug=n=>n.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const metric=(name,key,label)=>{const x=maps[key].get(name);if(!x)return `<div class="rank-metric"><b>—</b><span>${label}</span></div>`;return `<div class="rank-metric ${x.rank<=10?'rank-top10':''}"><b>#${x.rank}</b><span>${label} · ${x.value.toFixed(2)}%</span></div>`};
const rows=names.filter(n=>maps.wr.has(n)||maps.ban.has(n)||maps.pick.has(n)).map(name=>{const vals=['wr','ban','pick'].map(k=>maps[k].get(name)?.rank).filter(Number.isFinite);return {name,best:vals.length?Math.min(...vals):999}}).sort((a,b)=>a.best-b.best);
box.innerHTML=rows.length?rows.map(x=>`<a class="rank-card" href="../stats/heroes/${slug(x.name)}/"><div class="rank-card-head"><b>${x.name}</b><span class="rank-best">${x.best<=10?'TOP 10 EN ALGUNA MÉTRICA':'LIVE'}</span></div><div class="rank-metrics">${metric(x.name,'wr','WR')}${metric(x.name,'ban','BAN')}${metric(x.name,'pick','PICK')}</div></a>`).join(''):'<div class="empty">Tus héroes seguidos no aparecen en el snapshot live actual.</div>';
})();
</script>'''
html=html.replace('</body>',js+'</body>',1)
p.write_text(html,encoding='utf-8')
print('Enhanced My Meta with live WR, ban and pick rankings')
