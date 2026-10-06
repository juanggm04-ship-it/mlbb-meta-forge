from pathlib import Path

ROOT=Path('.')
out=ROOT/'my-meta'
out.mkdir(exist_ok=True)
html=r'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Meta · MLBB Meta Forge</title><meta name="description" content="Dashboard personal de MLBB Meta Forge con favoritos, watchlist, tendencias y picks de tu rol."><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 10% 0%,#172b52 0,transparent 30%),#070a12;color:#eef5ff;font-family:system-ui,-apple-system,Segoe UI,sans-serif}a{color:inherit;text-decoration:none}main{max-width:1120px;margin:auto;padding:28px 18px 70px}.top{display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap}.brand{font-weight:900;letter-spacing:.08em}.back{color:#57defa;font-size:13px}.hero{margin-top:28px;padding:28px;border:1px solid #273955;border-radius:26px;background:linear-gradient(145deg,#0d1728,#15142a)}.eyebrow{font-size:11px;font-weight:900;letter-spacing:.14em;color:#61e4ff}.hero h1{font-size:clamp(38px,7vw,68px);letter-spacing:-.055em;margin:10px 0}.hero p{color:#91a2bf;max-width:760px;line-height:1.6}.status{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.pill{border:1px solid #304463;border-radius:999px;padding:8px 11px;font-size:11px;color:#cbd8ec;background:#101a2b}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:18px}.panel{border:1px solid #263750;border-radius:20px;background:#0b1321;padding:18px}.panel h2{margin:4px 0 14px;font-size:20px}.panel small{color:#71809b;font-weight:900;letter-spacing:.11em}.cards{display:grid;gap:9px}.card{border:1px solid #24354f;border-radius:14px;padding:12px;background:#0e1727}.card-top{display:flex;justify-content:space-between;gap:10px;align-items:center}.card b{font-size:13px}.muted{color:#8292ad;font-size:11px}.metric{font-weight:900;font-size:12px}.up{color:#83e8b7}.down{color:#ff9d9d}.warn{color:#ffd071}.cyan{color:#5fe2ff}.empty{border:1px dashed #33445f;border-radius:14px;padding:14px;color:#7f8ea8;font-size:12px}.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.btn{display:inline-flex;padding:9px 12px;border:1px solid #31435f;border-radius:11px;background:#111a2b;color:#dce8fa;font-size:12px}.btn.primary{background:linear-gradient(135deg,#46e6ff,#8b5cff);color:#07101b;border:0;font-weight:900}.full{grid-column:1/-1}.table{display:grid;gap:8px}.row{display:grid;grid-template-columns:1.2fr .8fr .8fr .8fr;gap:8px;align-items:center;padding:10px;border:1px solid #24354f;border-radius:12px}.row span{font-size:11px}.row b{font-size:12px}.spark{width:110px;height:28px}@media(max-width:780px){.grid{grid-template-columns:1fr}.full{grid-column:auto}.row{grid-template-columns:1fr 1fr}.spark{width:100%}}
</style></head><body><main><div class="top"><a class="brand" href="../">MLBB FORGE</a><a class="back" href="../">← Volver a la portada</a></div><section class="hero"><div class="eyebrow">MY META</div><h1>Tu centro de mando.</h1><p id="intro">Reuniendo tu rol, favoritos, Watchlist y movimientos recientes del meta.</p><div id="status" class="status"></div><div class="actions"><a class="btn primary" href="../trends/">Explorar Trends</a><a class="btn" href="../#drafts">Abrir Draft Lab</a><button id="editProfile" class="btn" type="button">Editar preferencias</button></div></section><section class="grid"><article class="panel"><small>TUS HÉROES</small><h2>Favoritos y Watchlist</h2><div id="watch" class="cards"><div class="empty">Cargando…</div></div></article><article class="panel"><small>ROLE RADAR</small><h2 id="roleTitle">Picks para tu rol</h2><div id="rolePicks" class="cards"><div class="empty">Cargando…</div></div></article><article class="panel"><small>PULSE</small><h2>Cambios que importan</h2><div id="pulse" class="cards"><div class="empty">Buscando movimientos relevantes…</div></div></article><article class="panel"><small>EMERGING</small><h2>Subiendo en tu posición</h2><div id="emerging" class="cards"><div class="empty">Necesitamos historial para detectar tendencia.</div></div></article><article class="panel full"><small>OVERVIEW</small><h2>Resumen de tus héroes</h2><div id="overview" class="table"><div class="empty">Cargando…</div></div></article></section></main><script>
(async()=>{
const PROFILE='mf_profile_v1',WATCH='mf_watchlist_v1',SEEN='mf_watchlist_seen_v1';
const read=(k,f)=>{try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}catch{return f}};
const profile=read(PROFILE,null),watch=read(WATCH,[]),seen=read(SEEN,null);
const load=async p=>{try{const r=await fetch(p,{cache:'no-store'});if(!r.ok)return null;return await r.json()}catch{return null}};
const [cur,prev,hist]=await Promise.all([load('../data/live-meta.json'),load('../data/previous-meta.json'),load('../data/meta-history.json')]);
const heroes=cur?.heroes||[];const by=new Map(heroes.map(h=>[h.name,h]));const prevBy=new Map((prev?.heroes||[]).map(h=>[h.name,h]));
const allNames=[...new Set([...(profile?.heroes||[]),...(Array.isArray(watch)?watch:[])])];
const slug=n=>n.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const lane=profile?.role||null;document.getElementById('roleTitle').textContent=lane?`Picks para ${lane}`:'Picks para tu rol';
const st=document.getElementById('status');st.innerHTML=`<span class="pill">${lane?`Rol: ${lane}`:'Rol sin configurar'}</span><span class="pill">${allNames.length} héroes seguidos</span><span class="pill">Patch ${cur?.patch||'—'}</span><span class="pill">Snapshot ${cur?.updated||'—'}</span>`;
if(!profile){document.getElementById('intro').textContent='Configura tu rol y héroes favoritos desde la portada para personalizar este dashboard.'}
const delta=(a,b,k)=>a&&b&&Number.isFinite(a[k])&&Number.isFinite(b[k])?a[k]-b[k]:null;const fmt=d=>d==null?'—':`${d>0?'+':''}${d.toFixed(2)} pp`;
const watchBox=document.getElementById('watch');watchBox.innerHTML=allNames.length?allNames.map(n=>{const a=by.get(n),b=prevBy.get(n),d=delta(a,b,'wr');return `<a class="card" href="../heroes/${slug(n)}/"><div class="card-top"><b>${n}</b><span class="metric ${d>0.15?'up':d<-0.15?'down':''}">${fmt(d)} WR</span></div><div class="muted">${a?`${a.wr?.toFixed?.(2)??'—'}% WR · ${a.ban?.toFixed?.(2)??'—'}% ban`:'Sin dato actual'}</div></a>`}).join(''):'<div class="empty">Todavía no sigues héroes.</div>';
let roleHeroes=heroes.filter(h=>!lane||h.lane===lane).filter(h=>Number.isFinite(h.wr)).sort((a,b)=>b.wr-a.wr).slice(0,6);document.getElementById('rolePicks').innerHTML=roleHeroes.length?roleHeroes.map(h=>`<a class="card" href="../heroes/${slug(h.name)}/"><div class="card-top"><b>${h.name}</b><span class="metric cyan">${h.wr.toFixed(2)}% WR</span></div><div class="muted">${h.lane||'—'} · ${Number.isFinite(h.ban)?h.ban.toFixed(2)+'% ban':'ban —'}</div></a>`).join(''):'<div class="empty">No hay picks disponibles para este rol.</div>';
const pulse=[];for(const n of allNames){const a=by.get(n),b=prevBy.get(n);if(!a||!b)continue;const dw=delta(a,b,'wr'),db=delta(a,b,'ban');if(dw!=null&&Math.abs(dw)>=.35)pulse.push({n,t:`${fmt(dw)} WR`,w:Math.abs(dw),c:dw>0?'up':'down'});if(db!=null&&Math.abs(db)>=3)pulse.push({n,t:`${fmt(db)} ban`,w:Math.abs(db)/3,c:'warn'})}pulse.sort((a,b)=>b.w-a.w);document.getElementById('pulse').innerHTML=pulse.length?pulse.slice(0,6).map(x=>`<div class="card"><div class="card-top"><b>${x.n}</b><span class="metric ${x.c}">${x.t}</span></div></div>`).join(''):'<div class="empty">Sin cambios fuertes en tus héroes desde el snapshot anterior.</div>';
const snaps=Array.isArray(hist?.snapshots)?hist.snapshots:Array.isArray(hist)?hist:[];const series=new Map();for(const s of snaps){for(const h of s.heroes||[]){if(lane&&h.lane&&h.lane!==lane)continue;if(!series.has(h.name))series.set(h.name,[]);if(Number.isFinite(h.wr))series.get(h.name).push(h.wr)}}const emerg=[...series].map(([name,v])=>({name,v,d:v.length>=2?v.at(-1)-v[0]:0})).filter(x=>x.v.length>=2&&x.d>.25).sort((a,b)=>b.d-a.d).slice(0,6);document.getElementById('emerging').innerHTML=emerg.length?emerg.map(x=>`<a class="card" href="../heroes/${slug(x.name)}/"><div class="card-top"><b>${x.name}</b><span class="metric up">+${x.d.toFixed(2)} pp</span></div><div class="muted">${x.v.length} snapshots</div></a>`).join(''):'<div class="empty">Aún no hay suficiente historial para detectar picks emergentes con confianza.</div>';
const overview=document.getElementById('overview');overview.innerHTML=allNames.length?allNames.map(n=>{const a=by.get(n),b=prevBy.get(n);return `<a class="row" href="../heroes/${slug(n)}/"><b>${n}</b><span>${a?.wr?.toFixed?.(2)??'—'}% WR</span><span>${a?.ban?.toFixed?.(2)??'—'}% ban</span><span>${fmt(delta(a,b,'wr'))}</span></a>`}).join(''):'<div class="empty">Configura tus favoritos para llenar este resumen.</div>';
document.getElementById('editProfile').onclick=()=>{localStorage.removeItem('mf_onboarding_skipped_v1');localStorage.removeItem('mf_onboarding_done_v1');location.href='../?editProfile=1'};
})();
</script></body></html>'''
(out/'index.html').write_text(html,encoding='utf-8')
# append sitemap entry if generated
s=ROOT/'sitemap.xml'
if s.exists():
    text=s.read_text(encoding='utf-8')
    url='https://juanggm04-ship-it.github.io/mlbb-meta-forge/my-meta/'
    if url not in text:
        text=text.replace('</urlset>',f'<url><loc>{url}</loc></url></urlset>')
        s.write_text(text,encoding='utf-8')
# add home link when possible
p=ROOT/'index.html'
if p.exists():
    text=p.read_text(encoding='utf-8')
    if 'href="my-meta/"' not in text:
        needle='href="trends/"'
        pos=text.find(needle)
        if pos!=-1:
            end=text.find('</a>',pos)
            if end!=-1:
                end+=4
                text=text[:end]+'<a class="quick-action" href="my-meta/">◎ Mi Meta</a>'+text[end:]
        p.write_text(text,encoding='utf-8')
print('Generated My Meta dashboard')