from pathlib import Path

ROOT=Path('heroes')
if not ROOT.exists():
    raise RuntimeError('heroes directory not found')

CSS='''<style>
.hero-trend{margin-top:18px;padding:22px;border:1px solid #263552;border-radius:22px;background:linear-gradient(145deg,#0b1321,#12182a)}
.hero-trend-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap}.hero-trend-head h2{margin:4px 0}.trend-state{display:inline-flex;padding:7px 10px;border-radius:999px;border:1px solid #33425f;background:#101a2b;color:#dbe7f8;font-size:11px;font-weight:900}.trend-state.up{border-color:#2f6b58;color:#8be2b7}.trend-state.down{border-color:#71464a;color:#ffabab}.trend-state.stable{border-color:#39506e;color:#a9c9ff}.trend-state.volatile{border-color:#725b31;color:#ffd47b}.trend-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}.trend-card{padding:14px;border:1px solid #263650;border-radius:15px;background:#0a111d}.trend-card-head{display:flex;justify-content:space-between;gap:8px;align-items:baseline}.trend-card b{font-size:13px}.trend-card span{font-size:11px;color:#8796b1}.trend-svg{width:100%;height:82px;margin-top:9px;overflow:visible}.trend-svg polyline{fill:none;stroke:currentColor;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}.trend-svg circle{fill:currentColor}.trend-summary{margin-top:14px;color:#9aa9c2;line-height:1.6}.trend-note{margin-top:10px;color:#71809a;font-size:11px;line-height:1.5}@media(max-width:700px){.trend-grid{grid-template-columns:1fr}}
</style>'''

MARKUP='''<section id="heroTrend" class="hero-trend"><div class="hero-trend-head"><div><span class="label">TENDENCIA HISTÓRICA</span><h2>Evolución del héroe</h2></div><span id="heroTrendState" class="trend-state">Esperando historial</span></div><div id="heroTrendGrid" class="trend-grid"><div class="trend-card"><b>Historial insuficiente</b><span>Necesitamos al menos dos snapshots válidos.</span></div></div><p id="heroTrendSummary" class="trend-summary">La tendencia aparecerá cuando Meta Forge acumule suficientes puntos comparables.</p><p class="trend-note">Lectura editorial basada en snapshots históricos de WR, ban y pick. No implica causalidad ni predice el rendimiento de una partida concreta.</p></section>'''

JS=r'''<script>
(async()=>{
const root=document.getElementById('heroTrend'); if(!root)return;
const grid=document.getElementById('heroTrendGrid'),state=document.getElementById('heroTrendState'),summary=document.getElementById('heroTrendSummary');
const hero=document.querySelector('h1')?.textContent?.trim(); if(!hero)return;
let hist=null; try{const r=await fetch('../../data/meta-history.json',{cache:'no-store'});if(r.ok)hist=await r.json()}catch{}
const snaps=Array.isArray(hist?.snapshots)?hist.snapshots:[];
const pts=snaps.map(s=>({date:s.updated||s.fetched_at||'',patch:s.patch||'',h:(s.heroes||[]).find(x=>x.name===hero)})).filter(x=>x.h);
if(pts.length<2)return;
const vals=k=>pts.map(x=>Number.isFinite(x.h[k])?x.h[k]:null).filter(Number.isFinite);
const firstLast=k=>{const a=vals(k);return a.length>=2?a[a.length-1]-a[0]:null};
const range=k=>{const a=vals(k);return a.length?Math.max(...a)-Math.min(...a):0};
const avgStep=k=>{const a=vals(k);if(a.length<2)return 0;let s=0;for(let i=1;i<a.length;i++)s+=Math.abs(a[i]-a[i-1]);return s/(a.length-1)};
const wrD=firstLast('wr'),banD=firstLast('ban'),pickD=firstLast('pick');
const priorityD=(Number.isFinite(banD)?banD:0)+(Number.isFinite(pickD)?pickD:0);
let label='Fluctuando',cls='';
if(range('wr')>=1.5||avgStep('ban')>=4) {label='Volátil';cls='volatile'}
else if(Number.isFinite(wrD)&&wrD>=0.5){label='Subiendo';cls='up'}
else if(priorityD<=-3){label='Perdiendo prioridad';cls='down'}
else if(Number.isFinite(wrD)&&Math.abs(wrD)<=0.3&&Math.abs(priorityD)<=2){label='Estable';cls='stable'}
else if(Number.isFinite(wrD)&&wrD<=-0.5){label='Bajando';cls='down'}
state.textContent=label;state.className='trend-state '+cls;
function spark(key){
 const a=pts.map(x=>Number.isFinite(x.h[key])?x.h[key]:null);
 const clean=a.filter(Number.isFinite);if(clean.length<2)return '<span>Sin serie suficiente</span>';
 const min=Math.min(...clean),max=Math.max(...clean),span=Math.max(max-min,.01),w=260,h=72,p=6;
 const coords=[];a.forEach((v,i)=>{if(!Number.isFinite(v))return;const x=p+(w-2*p)*(i/Math.max(a.length-1,1));const y=h-p-(h-2*p)*((v-min)/span);coords.push([x,y])});
 const points=coords.map(c=>c.join(',')).join(' '),dots=coords.map(c=>`<circle cx="${c[0]}" cy="${c[1]}" r="2.7"></circle>`).join('');
 return `<svg class="trend-svg" viewBox="0 0 ${w} ${h}" role="img" aria-label="Evolución de ${key}"><polyline points="${points}"></polyline>${dots}</svg>`;
}
function latest(key){const a=vals(key);return a.length?a[a.length-1]:null}
function delta(key){const d=firstLast(key);return Number.isFinite(d)?`${d>0?'+':''}${d.toFixed(2)} pp`:'—'}
const cards=[['WR','wr'],['Ban','ban'],['Pick','pick']].map(([title,key])=>`<div class="trend-card"><div class="trend-card-head"><b>${title}</b><span>${Number.isFinite(latest(key))?latest(key).toFixed(2)+'%':'—'} · ${delta(key)}</span></div>${spark(key)}</div>`).join('');
grid.innerHTML=cards;
const oldest=pts[0],newest=pts[pts.length-1];
summary.textContent=`${hero} está ${label.toLowerCase()} en el historial disponible. Comparación: ${oldest.date||'inicio'} → ${newest.date||'actual'} · ${pts.length} snapshots. WR ${delta('wr')}, ban ${delta('ban')}, pick ${delta('pick')}.`;
})();
</script>'''

count=0
for page in ROOT.glob('*/index.html'):
    html=page.read_text(encoding='utf-8')
    if 'id="heroTrend"' in html:
        continue
    if '</head>' in html:
        html=html.replace('</head>',CSS+'</head>',1)
    anchor='<section class="box"><h2>Cómo interpretarlo</h2>'
    pos=html.find(anchor)
    if pos!=-1:
        html=html[:pos]+MARKUP+html[pos:]
    else:
        html=html.replace('</main>',MARKUP+'</main>',1)
    html=html.replace('</body>',JS+'</body>',1)
    page.write_text(html,encoding='utf-8')
    count+=1
print(f'Injected hero trends into {count} hero pages')
