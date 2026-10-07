from pathlib import Path
import json,re

ROOT=Path('.')
out=ROOT/'my-meta';out.mkdir(exist_ok=True)
index=ROOT/'index.html'
editorial={}
if index.exists():
    src=index.read_text(encoding='utf-8')
    m=re.search(r'const DATA=(\{.*?\});\nconst DRAFTS=',src,re.S)
    if m:
        try:
            d=json.loads(m.group(1))
            for h in d.get('heroes',[]):
                if h.get('name'):
                    editorial[h['name']]={'lane':h.get('lane'),'role':h.get('role'),'tier':h.get('tier')}
        except Exception:
            pass
EDITORIAL=json.dumps(editorial,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

html=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mi Meta · MLBB Meta Forge</title><meta name="description" content="Dashboard personal de MLBB Meta Forge con Watchlist live, tendencias y recomendaciones editoriales."><style>
:root{{color-scheme:dark}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 10% 0%,#172b52 0,transparent 30%),#070a12;color:#eef5ff;font-family:system-ui,-apple-system,Segoe UI,sans-serif}}a{{color:inherit;text-decoration:none}}button{{font:inherit}}main{{max-width:1120px;margin:auto;padding:28px 18px 70px}}.top{{display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap}}.brand{{font-weight:900;letter-spacing:.08em}}.back{{color:#57defa;font-size:13px}}.hero{{margin-top:28px;padding:28px;border:1px solid #273955;border-radius:26px;background:linear-gradient(145deg,#0d1728,#15142a)}}.eyebrow{{font-size:11px;font-weight:900;letter-spacing:.14em;color:#61e4ff}}.hero h1{{font-size:clamp(38px,7vw,68px);letter-spacing:-.055em;margin:10px 0}}.hero p{{color:#91a2bf;max-width:760px;line-height:1.6}}.status{{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}}.pill{{border:1px solid #304463;border-radius:999px;padding:8px 11px;font-size:11px;color:#cbd8ec;background:#101a2b}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:18px}}.panel{{border:1px solid #263750;border-radius:20px;background:#0b1321;padding:18px}}.panel h2{{margin:4px 0 14px;font-size:20px}}.panel small{{color:#71809b;font-weight:900;letter-spacing:.11em}}.cards{{display:grid;gap:9px}}.card{{border:1px solid #24354f;border-radius:14px;padding:12px;background:#0e1727}}.card-top{{display:flex;justify-content:space-between;gap:10px;align-items:center}}.card b{{font-size:13px}}.muted{{color:#8292ad;font-size:11px;line-height:1.5}}.metric{{font-weight:900;font-size:12px}}.up{{color:#83e8b7}}.down{{color:#ff9d9d}}.warn{{color:#ffd071}}.cyan{{color:#5fe2ff}}.empty{{border:1px dashed #33445f;border-radius:14px;padding:14px;color:#7f8ea8;font-size:12px}}.actions,.mini-actions{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}.btn{{display:inline-flex;align-items:center;padding:9px 12px;border:1px solid #31435f;border-radius:11px;background:#111a2b;color:#dce8fa;font-size:12px;cursor:pointer}}.btn.primary{{background:linear-gradient(135deg,#46e6ff,#8b5cff);color:#07101b;border:0;font-weight:900}}.btn.live{{border-color:#2e6470;color:#6be8ff}}.btn.editorial{{border-color:#6d5aa2;color:#c6adff}}.btn.danger{{color:#ffaaaa}}.full{{grid-column:1/-1}}.table{{display:grid;gap:8px}}.row{{display:grid;grid-template-columns:1.2fr .7fr .7fr .7fr auto;gap:8px;align-items:center;padding:10px;border:1px solid #24354f;border-radius:12px}}.row span{{font-size:11px}}.row b{{font-size:12px}}.tag{{display:inline-flex;margin-top:6px;padding:4px 7px;border:1px solid #32435f;border-radius:999px;font-size:9px;font-weight:900;color:#96a8c3}}.tag.ed{{border-color:#66508d;color:#c4a9ff}}@media(max-width:780px){{.grid{{grid-template-columns:1fr}}.full{{grid-column:auto}}.row{{grid-template-columns:1fr 1fr}}.row .row-actions{{grid-column:1/-1}}}}
</style></head><body><main><div class="top"><a class="brand" href="../">MLBB FORGE</a><a class="back" href="../">← Volver a la portada</a></div><section class="hero"><div class="eyebrow">MY META</div><h1>Tu centro de mando.</h1><p id="intro">Tu Watchlist puede incluir cualquier héroe del roster live. Las recomendaciones estratégicas solo aparecen donde existe perfil editorial curado.</p><div id="status" class="status"></div><div class="actions"><button class="btn primary" type="button" data-global-hero-search>＋ Buscar héroe</button><a class="btn" href="../trends/">Explorar Trends</a><a class="btn" href="../roster/">Live Roster</a><a class="btn" href="../#drafts">Draft Lab</a><button id="editProfile" class="btn" type="button">Editar preferencias</button></div></section><section class="grid"><article class="panel"><small>WATCHLIST LIVE</small><h2>Tus héroes</h2><div id="watch" class="cards"><div class="empty">Cargando…</div></div></article><article class="panel"><small>EDITORIAL ROLE RADAR</small><h2 id="roleTitle">Picks para tu rol</h2><div id="rolePicks" class="cards"><div class="empty">Cargando…</div></div></article><article class="panel"><small>LIVE PULSE</small><h2>Cambios que importan</h2><div id="pulse" class="cards"><div class="empty">Buscando movimientos relevantes…</div></div></article><article class="panel"><small>EDITORIAL EMERGING</small><h2>Subiendo en tu posición</h2><div id="emerging" class="cards"><div class="empty">Necesitamos historial para detectar tendencia.</div></div></article><article class="panel full"><small>OVERVIEW</small><h2>Resumen de tu Watchlist</h2><div id="overview" class="table"><div class="empty">Cargando…</div></div></article></section></main><script>
(async()=>{{
const EDITORIAL={EDITORIAL};
const PROFILE='mf_profile_v1',WATCH='mf_watchlist_v1';
const read=(k,f)=>{{try{{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}}catch{{return f}}}};
const write=(k,v)=>localStorage.setItem(k,JSON.stringify([...new Set(v)]));
const profile=read(PROFILE,null),watch=read(WATCH,[]);
const load=async p=>{{try{{const r=await fetch(p,{{cache:'no-store'}});if(!r.ok)return null;return await r.json()}}catch{{return null}}}};
const [cur,prev,hist]=await Promise.all([load('../data/live-meta.json'),load('../data/previous-meta.json'),load('../data/meta-history.json')]);
const heroes=cur?.heroes||[],by=new Map(heroes.map(h=>[h.name,h])),prevBy=new Map((prev?.heroes||[]).map(h=>[h.name,h]));
const allNames=[...new Set([...(profile?.heroes||[]),...(Array.isArray(watch)?watch:[])])].filter(n=>by.has(n));
const slug=n=>n.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const lane=profile?.role||null,roleTitle=document.getElementById('roleTitle');roleTitle.textContent=lane?`Picks editoriales para ${{lane}}`:'Picks editoriales para tu rol';
const st=document.getElementById('status');st.innerHTML=`<span class="pill">${{lane?`Rol: ${{lane}}`:'Rol sin configurar'}}</span><span class="pill">${{allNames.length}} héroes seguidos</span><span class="pill">${{Object.keys(EDITORIAL).length}} con perfil editorial</span><span class="pill">Patch ${{cur?.patch||'—'}}</span>`;
if(!profile)document.getElementById('intro').textContent='Puedes seguir cualquiera de los héroes live. Configura un rol para activar recomendaciones editoriales específicas.';
const delta=(a,b,k)=>a&&b&&Number.isFinite(a[k])&&Number.isFinite(b[k])?a[k]-b[k]:null,fmt=d=>d==null?'—':`${{d>0?'+':''}}${{d.toFixed(2)}} pp`,pct=v=>Number.isFinite(v)?v.toFixed(2)+'%':'—';
const hrefLive=n=>`../stats/heroes/${{slug(n)}}/`,hrefEd=n=>`../heroes/${{slug(n)}}/`;
const heroCard=n=>{{const a=by.get(n),b=prevBy.get(n),d=delta(a,b,'wr'),ed=EDITORIAL[n];return `<div class="card"><div class="card-top"><b>${{n}}</b><span class="metric ${{d>.15?'up':d<-.15?'down':''}}">${{fmt(d)}} WR</span></div><div class="muted">${{pct(a?.wr)}} WR · ${{pct(a?.ban)}} ban · ${{pct(a?.pick)}} pick</div><span class="tag ${{ed?'ed':''}}">${{ed?`EDITORIAL · ${{ed.lane||'—'}} · ${{ed.tier||'—'}}`:'LIVE STATS'}}</span><div class="mini-actions"><a class="btn live" href="${{hrefLive(n)}}">Stats</a>${{ed?`<a class="btn editorial" href="${{hrefEd(n)}}">Análisis</a>`:''}}<button class="btn danger" type="button" data-remove-watch="${{n}}">Quitar</button></div></div>`}};
const watchBox=document.getElementById('watch');function renderWatch(){{watchBox.innerHTML=allNames.length?allNames.map(heroCard).join(''):'<div class="empty">Todavía no sigues héroes. Usa “Buscar héroe” y síguelo desde su ficha live.</div>'}}renderWatch();
const editorialPool=Object.entries(EDITORIAL).map(([name,m])=>({{name,...m,live:by.get(name)}})).filter(x=>x.live&&Number.isFinite(x.live.wr));
let roleHeroes=editorialPool.filter(x=>!lane||x.lane===lane).sort((a,b)=>b.live.wr-a.live.wr).slice(0,6);document.getElementById('rolePicks').innerHTML=roleHeroes.length?roleHeroes.map(x=>`<div class="card"><div class="card-top"><b>${{x.name}}</b><span class="metric cyan">${{pct(x.live.wr)}} WR</span></div><div class="muted">${{x.lane||'—'}} · ${{x.role||'—'}} · tier ${{x.tier||'—'}}</div><div class="mini-actions"><a class="btn editorial" href="${{hrefEd(x.name)}}">Análisis</a><a class="btn live" href="${{hrefLive(x.name)}}">Stats</a></div></div>`).join(''):'<div class="empty">No hay picks editoriales disponibles para este rol.</div>';
const pulse=[];for(const n of allNames){{const a=by.get(n),b=prevBy.get(n);if(!a||!b)continue;const dw=delta(a,b,'wr'),db=delta(a,b,'ban'),dp=delta(a,b,'pick');if(dw!=null&&Math.abs(dw)>=.35)pulse.push({{n,t:`${{fmt(dw)}} WR`,w:Math.abs(dw),c:dw>0?'up':'down'}});if(db!=null&&Math.abs(db)>=3)pulse.push({{n,t:`${{fmt(db)}} ban`,w:Math.abs(db)/3,c:'warn'}});if(dp!=null&&Math.abs(dp)>=3)pulse.push({{n,t:`${{fmt(dp)}} pick`,w:Math.abs(dp)/3,c:'cyan'}})}}pulse.sort((a,b)=>b.w-a.w);document.getElementById('pulse').innerHTML=pulse.length?pulse.slice(0,8).map(x=>`<a class="card" href="${{hrefLive(x.n)}}"><div class="card-top"><b>${{x.n}}</b><span class="metric ${{x.c}}">${{x.t}}</span></div></a>`).join(''):'<div class="empty">Sin cambios fuertes en tu Watchlist desde el snapshot anterior.</div>';
const snaps=Array.isArray(hist?.snapshots)?hist.snapshots:Array.isArray(hist)?hist:[],allowed=new Set(editorialPool.filter(x=>!lane||x.lane===lane).map(x=>x.name)),series=new Map();for(const s of snaps){{for(const h of s.heroes||[]){{if(!allowed.has(h.name))continue;if(!series.has(h.name))series.set(h.name,[]);if(Number.isFinite(h.wr))series.get(h.name).push(h.wr)}}}}const emerg=[...series].map(([name,v])=>({{name,v,d:v.length>=2?v.at(-1)-v[0]:0}})).filter(x=>x.v.length>=2&&x.d>.25).sort((a,b)=>b.d-a.d).slice(0,6);document.getElementById('emerging').innerHTML=emerg.length?emerg.map(x=>`<a class="card" href="${{hrefEd(x.name)}}"><div class="card-top"><b>${{x.name}}</b><span class="metric up">+${{x.d.toFixed(2)}} pp</span></div><div class="muted">${{x.v.length}} snapshots · análisis editorial disponible</div></a>`).join(''):'<div class="empty">Aún no hay suficiente historial para detectar picks editoriales emergentes en tu rol.</div>';
const overview=document.getElementById('overview');overview.innerHTML=allNames.length?allNames.map(n=>{{const a=by.get(n),b=prevBy.get(n),ed=EDITORIAL[n];return `<div class="row"><b>${{n}}${{ed?'<span class="tag ed">EDITORIAL</span>':''}}</b><span>${{pct(a?.wr)}} WR</span><span>${{pct(a?.ban)}} ban</span><span>${{fmt(delta(a,b,'wr'))}}</span><span class="row-actions"><a class="btn live" href="${{hrefLive(n)}}">Abrir</a></span></div>`}}).join(''):'<div class="empty">Sigue héroes para llenar este resumen.</div>';
document.addEventListener('click',e=>{{const b=e.target.closest('[data-remove-watch]');if(!b)return;const name=b.dataset.removeWatch;write(WATCH,read(WATCH,[]).filter(x=>x!==name));location.reload()}});
document.getElementById('editProfile').onclick=()=>{{localStorage.removeItem('mf_onboarding_skipped_v1');localStorage.removeItem('mf_onboarding_done_v1');location.href='../?editProfile=1'}};
}})();
</script></body></html>'''
(out/'index.html').write_text(html,encoding='utf-8')

s=ROOT/'sitemap.xml'
if s.exists():
    text=s.read_text(encoding='utf-8');url='https://juanggm04-ship-it.github.io/mlbb-meta-forge/my-meta/'
    if url not in text:text=text.replace('</urlset>',f'<url><loc>{url}</loc></url></urlset>');s.write_text(text,encoding='utf-8')
p=ROOT/'index.html'
if p.exists():
    text=p.read_text(encoding='utf-8')
    if 'href="my-meta/"' not in text:
        pos=text.find('href="trends/"')
        if pos!=-1:
            end=text.find('</a>',pos)
            if end!=-1:text=text[:end+4]+'<a class="quick-action" href="my-meta/">◎ Mi Meta</a>'+text[end+4:]
        p.write_text(text,encoding='utf-8')
print(f'Generated My Meta dashboard with {len(editorial)} editorial profiles and full live Watchlist support')