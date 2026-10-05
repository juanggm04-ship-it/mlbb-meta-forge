from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="trendSpotlight"' in html:
    print('Meta trends already enhanced')
    raise SystemExit

css='''<style>
.trend-spotlight{margin-top:18px;padding:20px;border:1px solid #2b3b58;border-radius:20px;background:linear-gradient(145deg,#0b1321,#11172a)}
.trend-head{display:flex;justify-content:space-between;gap:14px;align-items:end;flex-wrap:wrap}.trend-head h3{margin:4px 0;font-size:24px}.trend-head p{margin:0;color:#8291aa;font-size:12px}.trend-columns{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:15px}.trend-card{border:1px solid #253650;border-radius:16px;background:#09111d;padding:14px}.trend-card h4{margin:0 0 10px;font-size:13px}.trend-item{display:grid;grid-template-columns:minmax(80px,1fr) 110px auto;gap:10px;align-items:center;padding:9px 0;border-top:1px solid #17243a}.trend-item:first-child{border-top:0}.trend-name{font-size:12px;font-weight:800}.trend-delta{font-size:11px;font-weight:900}.trend-delta.up{color:#82e7b3}.trend-delta.down{color:#ff9898}.spark{width:110px;height:30px;overflow:visible}.spark path{fill:none;stroke:currentColor;stroke-width:2.2;vector-effect:non-scaling-stroke}.spark line{stroke:#263650;stroke-width:1}.trend-empty{color:#74839d;font-size:11px;line-height:1.5}.trend-foot{margin-top:12px;color:#70809a;font-size:10px;line-height:1.5}@media(max-width:760px){.trend-columns{grid-template-columns:1fr}.trend-item{grid-template-columns:1fr 100px auto}.spark{width:100px}}
</style>'''
html=html.replace('</head>',css+'</head>')

markup='''<section id="trendSpotlight" class="trend-spotlight" aria-labelledby="trendSpotlightTitle"><div class="trend-head"><div><small>RISERS & FALLERS</small><h3 id="trendSpotlightTitle">Quién está moviendo el meta</h3></div><p id="trendRange">Esperando historial suficiente…</p></div><div class="trend-columns"><article class="trend-card"><h4>Risers</h4><div id="trendRisers"><p class="trend-empty">Se necesitan al menos dos snapshots válidos.</p></div></article><article class="trend-card"><h4>Fallers</h4><div id="trendFallers"><p class="trend-empty">Se necesitan al menos dos snapshots válidos.</p></div></article></div><p class="trend-foot">Las líneas muestran la evolución de win rate entre snapshots validados. No representan probabilidad futura ni una tendencia estadística formal.</p></section>'''
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
(async()=>{
const root=document.getElementById('trendSpotlight');if(!root)return;
const risers=document.getElementById('trendRisers'),fallers=document.getElementById('trendFallers'),range=document.getElementById('trendRange');
let hist=null;try{const r=await fetch('data/meta-history.json',{cache:'no-store'});if(r.ok)hist=await r.json()}catch{}
const snaps=hist?.snapshots;if(!Array.isArray(snaps)||snaps.length<2)return;
const last=snaps[snaps.length-1],prev=snaps[snaps.length-2];
const map=s=>new Map((s.heroes||[]).map(h=>[h.name,h]));const L=map(last),P=map(prev);
const rows=[];for(const [name,h] of L){const p=P.get(name);if(!p||!Number.isFinite(h.wr)||!Number.isFinite(p.wr))continue;rows.push({name,delta:h.wr-p.wr})}
const up=[...rows].sort((a,b)=>b.delta-a.delta).slice(0,5),down=[...rows].sort((a,b)=>a.delta-b.delta).slice(0,5);
function series(name){return snaps.map(s=>{const h=(s.heroes||[]).find(x=>x.name===name);return h&&Number.isFinite(h.wr)?h.wr:null}).filter(v=>v!==null).slice(-12)}
function spark(vals){if(vals.length<2)return '<span class="trend-empty">sin serie</span>';const w=110,h=30,pad=2,min=Math.min(...vals),max=Math.max(...vals),span=Math.max(max-min,.01);const pts=vals.map((v,i)=>{const x=pad+i*(w-pad*2)/(vals.length-1);const y=h-pad-(v-min)*(h-pad*2)/span;return [x,y]});const d=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');return `<svg class="spark" viewBox="0 0 ${w} ${h}" role="img" aria-label="Evolución de win rate"><line x1="0" y1="${h-1}" x2="${w}" y2="${h-1}"/><path d="${d}"/></svg>`}
function render(items,dir){return items.map(x=>`<div class="trend-item"><span class="trend-name">${x.name}</span>${spark(series(x.name))}<span class="trend-delta ${dir}">${x.delta>0?'+':''}${x.delta.toFixed(2)} pp</span></div>`).join('')||'<p class="trend-empty">Sin cambios comparables.</p>'}
risers.innerHTML=render(up,'up');fallers.innerHTML=render(down,'down');range.textContent=`${snaps.length} snapshots · ${snaps[0].updated||'inicio'} → ${last.updated||'actual'} · ${last.patch||'patch sin dato'}`;
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Enhanced meta trends with risers, fallers and sparklines')
