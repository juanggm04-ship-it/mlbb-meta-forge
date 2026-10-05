from pathlib import Path
import json

index=Path('index.html')
if not index.exists():
    raise RuntimeError('index.html not found')
html=index.read_text(encoding='utf-8')
if 'id="metaChanges"' in html:
    print('Meta changes already injected')
    raise SystemExit

css='''<style>
.meta-changes{margin-top:18px;padding:20px;border:1px solid #293955;border-radius:20px;background:linear-gradient(145deg,#0b1321,#12182a)}
.meta-changes-head{display:flex;justify-content:space-between;gap:14px;align-items:end;flex-wrap:wrap}.meta-changes-head h3{margin:4px 0;font-size:24px}.meta-changes-head p{margin:0;color:#8392ad;font-size:12px}.meta-change-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:16px}.meta-change-box{border:1px solid #253650;border-radius:15px;background:#0a111d;padding:14px}.meta-change-box h4{margin:0 0 10px;font-size:13px}.meta-change-list{display:grid;gap:8px}.meta-change-row{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:8px 9px;border-radius:10px;background:#0d1625}.meta-change-row b{font-size:12px}.meta-change-row span{font-size:11px;font-weight:800}.meta-change-row .up{color:#83e7b6}.meta-change-row .down{color:#ff9c9c}.meta-change-row .flat{color:#91a0ba}.meta-change-note{margin-top:12px;color:#73829d;font-size:11px;line-height:1.5}.meta-change-tags{display:flex;gap:7px;flex-wrap:wrap}.meta-change-tag{padding:7px 9px;border-radius:999px;border:1px solid #30415e;background:#101a2b;color:#c9d6e9;font-size:11px}@media(max-width:760px){.meta-change-grid{grid-template-columns:1fr}}
</style>'''
html=html.replace('</head>',css+'</head>')

markup='''<section id="metaChanges" class="meta-changes" aria-labelledby="metaChangesTitle"><div class="meta-changes-head"><div><small>META MOVES</small><h3 id="metaChangesTitle">Qué cambió desde el snapshot anterior</h3></div><p id="metaChangesPeriod">Esperando dos snapshots comparables…</p></div><div id="metaChangesBody" class="meta-change-grid"><div class="meta-change-box"><h4>Sin comparación todavía</h4><p class="meta-change-note">Cuando exista un snapshot anterior validado, aquí aparecerán cambios reales de win rate, ban rate y entradas/salidas del top.</p></div></div><p class="meta-change-note">Los deltas se muestran en puntos porcentuales. Un cambio pequeño no implica por sí solo una tendencia estable.</p></section>'''
anchor='id="dataHealth"'
pos=html.find(anchor)
if pos!=-1:
    end=html.find('</section>',pos)
    if end!=-1:
        end+=10
        html=html[:end]+markup+html[end:]
else:
    # fallback: put before first main closing
    html=html.replace('</main>',markup+'</main>',1)

js=r'''<script>
(async()=>{
const root=document.getElementById('metaChanges'),body=document.getElementById('metaChangesBody'),period=document.getElementById('metaChangesPeriod');
if(!root||!body)return;
const load=async path=>{try{const r=await fetch(path,{cache:'no-store'});if(!r.ok)return null;return await r.json()}catch{return null}};
const [cur,prev]=await Promise.all([load('data/live-meta.json'),load('data/previous-meta.json')]);
if(!cur||!prev||!Array.isArray(cur.heroes)||!Array.isArray(prev.heroes))return;
const by=(arr)=>new Map(arr.map(h=>[h.name,h]));
const C=by(cur.heroes),P=by(prev.heroes);
const rows=[];
for(const [name,c] of C){const p=P.get(name);if(!p)continue;rows.push({name,wr:(Number.isFinite(c.wr)&&Number.isFinite(p.wr))?c.wr-p.wr:null,ban:(Number.isFinite(c.ban)&&Number.isFinite(p.ban))?c.ban-p.ban:null,pick:(Number.isFinite(c.pick)&&Number.isFinite(p.pick))?c.pick-p.pick:null,c,p})}
const fmt=v=>`${v>0?'+':''}${v.toFixed(2)} pp`;
const list=(items,key)=>items.map(x=>`<div class="meta-change-row"><b>${x.name}</b><span class="${x[key]>0?'up':x[key]<0?'down':'flat'}">${fmt(x[key])}</span></div>`).join('');
const wrValid=rows.filter(x=>Number.isFinite(x.wr));
const banValid=rows.filter(x=>Number.isFinite(x.ban));
const wrUp=[...wrValid].sort((a,b)=>b.wr-a.wr).slice(0,5);
const wrDown=[...wrValid].sort((a,b)=>a.wr-b.wr).slice(0,5);
const banMoves=[...banValid].sort((a,b)=>Math.abs(b.ban)-Math.abs(a.ban)).slice(0,5);
const top=(arr,n=15)=>new Set([...arr].sort((a,b)=>(b.wr??-1)-(a.wr??-1)).slice(0,n).map(h=>h.name));
const topC=top(cur.heroes),topP=top(prev.heroes);
const entered=[...topC].filter(n=>!topP.has(n));
const left=[...topP].filter(n=>!topC.has(n));
period.textContent=`${prev.updated||'snapshot anterior'} → ${cur.updated||'snapshot actual'} · ${cur.patch||'patch sin dato'}`;
body.innerHTML=`
<div class="meta-change-box"><h4>Mayores subidas de WR</h4><div class="meta-change-list">${wrUp.length?list(wrUp,'wr'):'<span class="flat">Sin datos comparables</span>'}</div></div>
<div class="meta-change-box"><h4>Mayores bajadas de WR</h4><div class="meta-change-list">${wrDown.length?list(wrDown,'wr'):'<span class="flat">Sin datos comparables</span>'}</div></div>
<div class="meta-change-box"><h4>Movimientos fuertes de ban rate</h4><div class="meta-change-list">${banMoves.length?list(banMoves,'ban'):'<span class="flat">Sin datos comparables</span>'}</div></div>
<div class="meta-change-box"><h4>Cambios en el Top 15 por WR</h4><div class="meta-change-tags">${entered.map(n=>`<span class="meta-change-tag">↑ Entró ${n}</span>`).join('')}${left.map(n=>`<span class="meta-change-tag">↓ Salió ${n}</span>`).join('')||(!entered.length?'<span class="meta-change-tag">Sin cambios de entrada/salida</span>':'')}</div></div>`;
})();
</script>'''
html=html.replace('</body>',js+'</body>')
index.write_text(html,encoding='utf-8')
print('Injected meta snapshot comparison panel')
