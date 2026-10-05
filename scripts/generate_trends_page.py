from pathlib import Path
import json,re,html

ROOT=Path('.')
INDEX=ROOT/'index.html'
OUT=ROOT/'trends'/'index.html'

if not INDEX.exists():
    raise RuntimeError('index.html not found')

src=INDEX.read_text(encoding='utf-8')
m=re.search(r'const DATA=(\{.*?\});\nconst DRAFTS=',src,re.S)
if not m:
    raise RuntimeError('Could not locate DATA object in index.html')
data=json.loads(m.group(1))
heroes=data.get('heroes',[])
if not heroes:
    raise RuntimeError('No heroes found in DATA')

pool=[{'name':h.get('name'),'lane':h.get('lane'),'role':h.get('role'),'tier':h.get('tier')} for h in heroes if h.get('name')]
pool_json=json.dumps(pool,ensure_ascii=False,separators=(',',':'))

page=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MLBB Trends · Meta Forge</title><meta name="description" content="Tendencias del meta MLBB: héroes que suben, bajan, ganan prioridad de ban y evolucionan por rol."><link rel="canonical" href="https://juanggm04-ship-it.github.io/mlbb-meta-forge/trends/"><style>
:root{{--bg:#070a12;--card:#0d1423;--line:#24324c;--text:#edf4ff;--muted:#8796b1;--cyan:#46e6ff;--green:#83e7b6;--red:#ff9c9c;--gold:#ffd36c}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 12% 0%,#152547 0,transparent 30%),var(--bg);color:var(--text);font-family:system-ui,-apple-system,sans-serif}}a{{color:inherit;text-decoration:none}}main{{max-width:1180px;margin:auto;padding:28px 18px 60px}}.top{{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}}.back{{color:var(--cyan);font-weight:800}}.hero{{margin-top:22px;padding:30px;border:1px solid var(--line);border-radius:28px;background:linear-gradient(145deg,#0d1627,#17132b)}}.eyebrow{{color:var(--cyan);font-size:11px;font-weight:900;letter-spacing:.12em}}h1{{font-size:clamp(42px,8vw,76px);line-height:.95;letter-spacing:-.06em;margin:12px 0}}p{{color:#a7b4ca;line-height:1.65}}.filters{{display:grid;grid-template-columns:1.3fr repeat(2,.8fr);gap:10px;margin-top:18px}}input,select{{width:100%;background:#0a111e;border:1px solid #2b3b58;color:var(--text);border-radius:12px;padding:12px 13px}}.status{{margin-top:14px;color:var(--muted);font-size:12px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:18px}}.panel{{padding:18px;border:1px solid var(--line);border-radius:19px;background:#0a111e}}.panel h2{{margin:0 0 12px;font-size:19px}}.list{{display:grid;gap:8px}}.row{{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:10px;align-items:center;padding:10px 11px;border:1px solid #22314a;border-radius:12px;background:#0d1625}}.row b{{font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.meta{{font-size:10px;color:var(--muted)}}.delta{{font-size:12px;font-weight:900}}.up{{color:var(--green)}}.down{{color:var(--red)}}.flat{{color:#9aa8be}}.spark{{width:90px;height:28px}}.all{{margin-top:14px;padding:18px;border:1px solid var(--line);border-radius:19px;background:#0a111e}}.table{{display:grid;gap:7px;margin-top:12px}}.trow{{display:grid;grid-template-columns:minmax(130px,1.4fr) .7fr .7fr .7fr .8fr;gap:9px;align-items:center;padding:10px 12px;border-bottom:1px solid #182338}}.trow.head{{font-size:10px;color:var(--muted);font-weight:900;letter-spacing:.08em}}.pill{{display:inline-flex;padding:5px 8px;border:1px solid #30415e;border-radius:999px;font-size:10px;color:#c9d5e7}}.empty{{color:var(--muted);font-size:12px;padding:14px 0}}@media(max-width:760px){{.filters,.grid{{grid-template-columns:1fr}}.trow{{grid-template-columns:1.3fr .8fr .8fr}}.hide-mob{{display:none}}.spark{{width:70px}}}}</style></head><body><main><div class="top"><a class="back" href="../">← Meta Forge</a><a class="pill" href="../heroes/">Fichas de héroes</a></div><section class="hero"><div class="eyebrow">META TRENDS</div><h1>Quién sube. Quién cae.</h1><p>Compara snapshots validados del meta. Filtra por línea o rol y revisa win rate, ban priority y evolución histórica sin convertir dos puntos en una profecía.</p><div class="filters"><input id="q" type="search" placeholder="Buscar héroe…"><select id="lane"><option value="">Todas las líneas</option></select><select id="role"><option value="">Todos los roles</option></select></div><div id="status" class="status">Cargando historial…</div></section><section class="grid"><article class="panel"><h2>📈 Risers</h2><div id="risers" class="list"></div></article><article class="panel"><h2>📉 Fallers</h2><div id="fallers" class="list"></div></article><article class="panel"><h2>🚨 Ban priority</h2><div id="banmoves" class="list"></div></article><article class="panel"><h2>🔥 Más disputados ahora</h2><div id="contested" class="list"></div></article></section><section class="all"><h2>Explorador de tendencias</h2><div class="table"><div class="trow head"><span>HÉROE</span><span>WR Δ</span><span>BAN Δ</span><span class="hide-mob">WR ACTUAL</span><span class="hide-mob">TENDENCIA</span></div><div id="allRows"></div></div></section></main><script>
const POOL={pool_json};
const slug=n=>n.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const load=async p=>{{try{{const r=await fetch(p,{{cache:'no-store'}});return r.ok?await r.json():null}}catch{{return null}}}};
const fmt=v=>Number.isFinite(v)?`${{v>0?'+':''}}${{v.toFixed(2)}} pp`:'—';
const spark=vals=>{{vals=vals.filter(Number.isFinite);if(vals.length<2)return '<span class="meta">sin serie</span>';const w=90,h=28,min=Math.min(...vals),max=Math.max(...vals),d=(max-min)||1;const pts=vals.map((v,i)=>`${{(i/(vals.length-1))*w}},${{h-3-((v-min)/d)*(h-6)}}`).join(' ');return `<svg class="spark" viewBox="0 0 ${{w}} ${{h}}" aria-hidden="true"><polyline fill="none" stroke="currentColor" stroke-width="2" points="${{pts}}"/></svg>`}};
function classify(series){{const v=series.filter(Number.isFinite);if(v.length<2)return 'Sin serie';const d=v.at(-1)-v[0];const range=Math.max(...v)-Math.min(...v);if(range>=2.5)return 'Volátil';if(d>=0.6)return 'Subiendo';if(d<=-0.6)return 'Bajando';return 'Estable'}}
(async()=>{{
 const [cur,prev,hist]=await Promise.all([load('../data/live-meta.json'),load('../data/previous-meta.json'),load('../data/meta-history.json')]);
 const C=new Map((cur?.heroes||[]).map(h=>[h.name,h])),P=new Map((prev?.heroes||[]).map(h=>[h.name,h]));
 const H=Array.isArray(hist)?hist:[];
 const byName=new Map(POOL.map(h=>[h.name,h]));
 const rows=POOL.map(meta=>{{const c=C.get(meta.name),p=P.get(meta.name);const series=H.map(s=>(s.heroes||[]).find(x=>x.name===meta.name)?.wr).filter(Number.isFinite);return {{...meta,c,p,wrDelta:c&&p&&Number.isFinite(c.wr)&&Number.isFinite(p.wr)?c.wr-p.wr:null,banDelta:c&&p&&Number.isFinite(c.ban)&&Number.isFinite(p.ban)?c.ban-p.ban:null,series}}}});
 const lanes=[...new Set(POOL.map(h=>h.lane).filter(Boolean))].sort(),roles=[...new Set(POOL.map(h=>h.role).filter(Boolean))].sort();
 lane.innerHTML+=[...lanes].map(x=>`<option>${{x}}</option>`).join('');role.innerHTML+=[...roles].map(x=>`<option>${{x}}</option>`).join('');
 const card=(r,key)=>`<a class="row" href="../heroes/${{slug(r.name)}}/"><div><b>${{r.name}}</b><div class="meta">${{r.lane||'—'}} · ${{r.role||'—'}}</div></div><span class="delta ${{r[key]>0?'up':r[key]<0?'down':'flat'}}">${{fmt(r[key])}}</span><span class="${{r[key]>=0?'up':'down'}}">${{spark(r.series)}}</span></a>`;
 function filtered(){{const qq=q.value.trim().toLowerCase();return rows.filter(r=>(!qq||r.name.toLowerCase().includes(qq))&&(!lane.value||r.lane===lane.value)&&(!role.value||r.role===role.value))}}
 function render(){{const f=filtered();const wr=f.filter(r=>Number.isFinite(r.wrDelta)),ban=f.filter(r=>Number.isFinite(r.banDelta)),now=f.filter(r=>r.c&&Number.isFinite(r.c.ban));risers.innerHTML=[...wr].sort((a,b)=>b.wrDelta-a.wrDelta).slice(0,6).map(r=>card(r,'wrDelta')).join('')||'<div class="empty">Esperando comparación suficiente.</div>';fallers.innerHTML=[...wr].sort((a,b)=>a.wrDelta-b.wrDelta).slice(0,6).map(r=>card(r,'wrDelta')).join('')||'<div class="empty">Esperando comparación suficiente.</div>';banmoves.innerHTML=[...ban].sort((a,b)=>Math.abs(b.banDelta)-Math.abs(a.banDelta)).slice(0,6).map(r=>card(r,'banDelta')).join('')||'<div class="empty">Esperando comparación suficiente.</div>';contested.innerHTML=[...now].sort((a,b)=>b.c.ban-a.c.ban).slice(0,6).map(r=>`<a class="row" href="../heroes/${{slug(r.name)}}/"><div><b>${{r.name}}</b><div class="meta">${{r.lane||'—'}} · ${{r.role||'—'}}</div></div><span class="delta">${{r.c.ban.toFixed(2)}}%</span><span>${{spark(r.series)}}</span></a>`).join('')||'<div class="empty">Sin ban rate disponible.</div>';allRows.innerHTML=f.sort((a,b)=>(b.c?.wr??-1)-(a.c?.wr??-1)).map(r=>`<a class="trow" href="../heroes/${{slug(r.name)}}/"><span><b>${{r.name}}</b><div class="meta">${{r.lane||'—'}} · ${{r.role||'—'}}</div></span><span class="${{r.wrDelta>0?'up':r.wrDelta<0?'down':'flat'}}">${{fmt(r.wrDelta)}}</span><span class="${{r.banDelta>0?'up':r.banDelta<0?'down':'flat'}}">${{fmt(r.banDelta)}}</span><span class="hide-mob">${{Number.isFinite(r.c?.wr)?r.c.wr.toFixed(2)+'%':'—'}}</span><span class="hide-mob">${{classify(r.series)}}</span></a>`).join('')||'<div class="empty">No hay héroes con esos filtros.</div>';status.textContent=`${{f.length}} héroes del pool editorial · ${{H.length}} snapshots históricos · ${{cur?.patch||'patch sin dato'}}`;}}
 q.oninput=lane.onchange=role.onchange=render;render();
}})();
</script></body></html>'''

OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(page,encoding='utf-8')

# Add a Trends shortcut to the homepage without disturbing existing JS navigation.
home=INDEX.read_text(encoding='utf-8')
if 'href="trends/"' not in home:
    quick='<a class="quick-action" href="trends/"><b>↗ Meta Trends</b><span>Risers, fallers, ban priority e historial por héroe.</span></a>'
    marker='<div id="homeQuickActions" class="quick-actions">'
    if marker in home:
        home=home.replace(marker,marker+quick,1)
    INDEX.write_text(home,encoding='utf-8')

# Add Trends to sitemap if present.
smap=ROOT/'sitemap.xml'
if smap.exists():
    s=smap.read_text(encoding='utf-8')
    url='<url><loc>https://juanggm04-ship-it.github.io/mlbb-meta-forge/trends/</loc></url>'
    if '/trends/' not in s:
        s=s.replace('</urlset>',url+'</urlset>')
        smap.write_text(s,encoding='utf-8')
print(f'Generated global trends page for {len(pool)} editorial heroes')
