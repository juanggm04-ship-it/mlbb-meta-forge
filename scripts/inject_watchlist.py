from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="watchlistPanel"' in html:
    print('Watchlist already injected')
    raise SystemExit

css='''<style>
.watchlist{margin-top:18px;padding:20px;border:1px solid #2a3a56;border-radius:20px;background:linear-gradient(145deg,#0a1220,#121a2b)}
.watchlist-head{display:flex;justify-content:space-between;gap:12px;align-items:end;flex-wrap:wrap}.watchlist-head h3{margin:4px 0;font-size:24px}.watchlist-head p{margin:0;color:#8392ac;font-size:12px}.watch-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:14px}.watch-card{border:1px solid #263752;border-radius:15px;background:#0c1422;padding:14px}.watch-card b{display:block}.watch-card span{display:block;margin-top:4px;color:#8797b2;font-size:11px}.watch-card strong{display:inline-block;margin-top:8px;font-size:12px}.watch-card .up{color:#82e6b5}.watch-card .down{color:#ff9e9e}.watch-card .flat{color:#94a4bf}.watch-empty{padding:16px;border:1px dashed #30415e;border-radius:14px;color:#7f8eaa;font-size:12px}.watch-link{display:inline-flex;margin-top:9px;color:#46e6ff;font-size:11px;text-decoration:none}.watch-remove{margin-top:8px;border:1px solid #33445f;background:#111a2c;color:#dce7f8;border-radius:9px;padding:7px 9px;cursor:pointer;font-size:11px}@media(max-width:900px){.watch-grid{grid-template-columns:1fr 1fr}}@media(max-width:640px){.watch-grid{grid-template-columns:1fr}}
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
const slug=n=>n.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
async function load(path){try{const r=await fetch(path,{cache:'no-store'});if(!r.ok)return null;return await r.json()}catch{return null}}
async function render(){
 const box=document.getElementById('watchGrid');if(!box)return;
 const names=get();if(!names.length){box.innerHTML='<div class="watch-empty">Aún no sigues héroes. Añádelos desde una ficha o desde Meta Trends.</div>';return}
 const [cur,prev]=await Promise.all([load('data/live-meta.json'),load('data/previous-meta.json')]);
 const c=new Map((cur?.heroes||[]).map(h=>[h.name,h])),p=new Map((prev?.heroes||[]).map(h=>[h.name,h]));
 box.innerHTML=names.map(name=>{const a=c.get(name),b=p.get(name);const d=(a&&b&&Number.isFinite(a.wr)&&Number.isFinite(b.wr))?a.wr-b.wr:null;const cls=d>0.15?'up':d<-0.15?'down':'flat';const text=d==null?'Sin comparación todavía':`${d>0?'+':''}${d.toFixed(2)} pp WR`;return `<article class="watch-card"><b>${name}</b><span>${a?`${a.wr?.toFixed?.(2)??'—'}% WR · ${a.ban?.toFixed?.(2)??'—'}% ban`:'Sin snapshot actual'}</span><strong class="${cls}">${text}</strong><a class="watch-link" href="heroes/${slug(name)}/">Ver tendencia →</a><button class="watch-remove" data-remove="${name.replace(/"/g,'&quot;')}">Quitar</button></article>`}).join('');
 box.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{set(get().filter(n=>n!==b.dataset.remove));render()});
}
window.MFWatchlist={get,set,add(name){set([...get(),name]);render()},remove(name){set(get().filter(n=>n!==name));render()},has(name){return get().includes(name)},render};
render();
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Injected homepage watchlist')
