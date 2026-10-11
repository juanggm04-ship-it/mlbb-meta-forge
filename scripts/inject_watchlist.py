from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="watchlistPanel"' in html:
    print('Watchlist already injected')
    raise SystemExit

css='''<style>
.watchlist{margin-top:18px;padding:20px;border:1px solid #2a3a56;border-radius:20px;background:linear-gradient(145deg,#0a1220,#121a2b)}
.watchlist-head{display:flex;justify-content:space-between;gap:12px;align-items:end;flex-wrap:wrap}.watchlist-head h3{margin:4px 0;font-size:24px}.watchlist-head p{margin:0;color:#8392ac;font-size:12px}.watch-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:14px}.watch-card{border:1px solid #263752;border-radius:15px;background:#0c1422;padding:14px}.watch-card b{display:block}.watch-card span{display:block;margin-top:4px;color:#8797b2;font-size:11px}.watch-card strong{display:inline-block;margin-top:8px;font-size:12px}.watch-card .up{color:#82e6b5}.watch-card .down{color:#ff9e9e}.watch-card .flat{color:#94a4bf}.watch-empty{padding:16px;border:1px dashed #30415e;border-radius:14px;color:#7f8eaa;font-size:12px}.watch-links{display:flex;gap:9px;flex-wrap:wrap;margin-top:9px}.watch-link{display:inline-flex;color:#46e6ff;font-size:11px;text-decoration:none}.watch-link.editorial{color:#c9b2ff}.watch-tag{display:inline-flex!important;width:max-content;margin-top:7px!important;padding:4px 7px;border:1px solid #34506e;border-radius:999px;color:#91a6c3!important;font-size:9px!important;font-weight:900}.watch-tag.editorial{border-color:#66508d;color:#c4a9ff!important}.watch-remove{margin-top:8px;border:1px solid #33445f;background:#111a2c;color:#dce7f8;border-radius:9px;padding:7px 9px;cursor:pointer;font-size:11px}@media(max-width:900px){.watch-grid{grid-template-columns:1fr 1fr}}@media(max-width:640px){.watch-grid{grid-template-columns:1fr}}
</style>'''
html=html.replace('</head>',css+'</head>')

markup='''<section id="watchlistPanel" class="watchlist" aria-labelledby="watchlistTitle"><div class="watchlist-head"><div><small>MY WATCHLIST</small><h3 id="watchlistTitle">Héroes que sigues</h3></div><p>Cambios guardados solo en este navegador.</p></div><div id="watchGrid" class="watch-grid"><div class="watch-empty">Añade héroes desde sus fichas o desde la página Trends.</div></div></section>'''
anchor='id="metaChanges"'
pos=html.find(anchor)
if pos!=-1:
    end=html.find('</section>',pos)
    if end!=-1:
        end+=10
        html=html[:end]+markup+html[end:]
else:
    html=html.replace('</main>',markup+'</main>',1)

js=r'''<script>
(()=>{
const KEY='mf_watchlist_v1';
const get=()=>{try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch{return []}};
const set=v=>localStorage.setItem(KEY,JSON.stringify([...new Set(v)]));
const norm=n=>(n||'').toLowerCase().replace(/&/g,'and').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'');
const slug=n=>n.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
async function load(path){try{const r=await fetch(path,{cache:'no-store'});if(!r.ok)return null;return await r.json()}catch{return null}}
async function render(){
 const box=document.getElementById('watchGrid');if(!box)return;
 const names=get();if(!names.length){box.innerHTML='<div class="watch-empty">Aún no sigues héroes. Añádelos desde una ficha o desde Meta Trends.</div>';return}
 const [cur,prev,cat]=await Promise.all([load('data/live-meta.json'),load('data/previous-meta.json'),load('data/hero-catalog.json')]);
 const c=new Map((cur?.heroes||[]).filter(h=>h.name).map(h=>[norm(h.name),h])),p=new Map((prev?.heroes||[]).filter(h=>h.name).map(h=>[norm(h.name),h])),ed=new Map((cat?.heroes||[]).filter(h=>h.name).map(h=>[norm(h.name),h]));
 box.innerHTML=names.map(stored=>{const key=norm(stored),a=c.get(key),b=p.get(key),e=ed.get(key),name=a?.name||stored;const d=(a&&b&&Number.isFinite(a.wr)&&Number.isFinite(b.wr))?a.wr-b.wr:null;const cls=d>0.15?'up':d<-0.15?'down':'flat';const text=d==null?'Sin comparación todavía':`${d>0?'+':''}${d.toFixed(2)} pp WR`;const editorial=e?`<span class="watch-tag editorial">EDITORIAL · ${e.lane||'—'} · ${e.tier||'—'}</span>`:'<span class="watch-tag">LIVE STATS</span>';const analysis=e?`<a class="watch-link editorial" href="heroes/${slug(e.name)}/">Análisis editorial →</a>`:'';return `<article class="watch-card"><b>${name}</b><span>${a?`${a.wr?.toFixed?.(2)??'—'}% WR · ${a.ban?.toFixed?.(2)??'—'}% ban · ${a.pick?.toFixed?.(2)??'—'}% pick`:'Sin snapshot actual'}</span>${editorial}<strong class="${cls}">${text}</strong><div class="watch-links"><a class="watch-link" href="stats/heroes/${slug(name)}/">Stats live →</a>${analysis}</div><button class="watch-remove" data-remove="${stored.replace(/"/g,'&quot;')}">Quitar</button></article>`}).join('');
 box.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{set(get().filter(n=>n!==b.dataset.remove));render()});
}
window.MFWatchlist={get,set,add(name){set([...get(),name]);render()},remove(name){set(get().filter(n=>n!==name));render()},has(name){const k=norm(name);return get().some(n=>norm(n)===k)},render};
render();
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Injected homepage Watchlist with normalized full-live stats links and optional editorial analysis')