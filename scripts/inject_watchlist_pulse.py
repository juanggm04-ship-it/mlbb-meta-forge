from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="watchlistPulse"' in html:
    print('Watchlist Pulse already injected')
    raise SystemExit

css='''<style>
.watch-pulse{margin-top:12px;padding:16px 18px;border:1px solid #33425f;border-radius:18px;background:linear-gradient(145deg,#0b1423,#151528)}
.watch-pulse[hidden]{display:none}.watch-pulse-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.watch-pulse-head h4{margin:3px 0;font-size:17px}.watch-pulse-head p{margin:0;color:#8291aa;font-size:11px}.pulse-count{display:inline-flex;min-width:28px;height:28px;padding:0 8px;align-items:center;justify-content:center;border-radius:999px;background:#46e6ff;color:#07101b;font-size:11px;font-weight:900}.pulse-list{display:grid;gap:8px;margin-top:12px}.pulse-item{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:10px 11px;border:1px solid #263750;border-radius:12px;background:#0c1422}.pulse-item b{font-size:12px}.pulse-item span{font-size:11px;font-weight:800;text-align:right}.pulse-up{color:#83e7b6}.pulse-down{color:#ff9d9d}.pulse-ban{color:#ffcf70}.pulse-pick{color:#c9a7ff}.pulse-rank{color:#69dfff}.pulse-note{margin-top:10px;color:#72819b;font-size:10px;line-height:1.5}
</style>'''
html=html.replace('</head>',css+'</head>')

markup='''<section id="watchlistPulse" class="watch-pulse" hidden aria-labelledby="watchPulseTitle"><div class="watch-pulse-head"><div><small>WATCHLIST PULSE</small><h4 id="watchPulseTitle">Cambios desde tu última visita</h4><p id="watchPulsePeriod"></p></div><span id="watchPulseCount" class="pulse-count">0</span></div><div id="watchPulseList" class="pulse-list"></div><p class="pulse-note">Solo mostramos movimientos relevantes. Los rankings comparan el roster live completo y el estado se guarda localmente después de esta lectura.</p></section>'''
anchor='id="watchlistPanel"'
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
const WATCH='mf_watchlist_v1',SEEN='mf_watchlist_seen_v2';
const panel=document.getElementById('watchlistPulse'),list=document.getElementById('watchPulseList'),count=document.getElementById('watchPulseCount'),period=document.getElementById('watchPulsePeriod');
if(!panel||!list)return;
const read=(k,f)=>{try{return JSON.parse(localStorage.getItem(k)||JSON.stringify(f))}catch{return f}};
const watched=read(WATCH,[]);if(!Array.isArray(watched)||!watched.length)return;
let cur=null;try{const r=await fetch('data/live-meta.json',{cache:'no-store'});if(r.ok)cur=await r.json()}catch{}
if(!cur||!Array.isArray(cur.heroes))return;
const rankMap=key=>new Map([...cur.heroes].filter(h=>Number.isFinite(h[key])).sort((a,b)=>b[key]-a[key]).map((h,i)=>[h.name,i+1]));
const ranks={wr:rankMap('wr'),ban:rankMap('ban'),pick:rankMap('pick')};
const map=new Map(cur.heroes.map(h=>[h.name,h]));
const previous=read(SEEN,null);
const snapshotId=cur.fetched_at||cur.updated||cur.patch||'unknown';
const nowState={snapshot:snapshotId,updated:cur.updated||'',patch:cur.patch||'',heroes:{}};
for(const name of watched){const h=map.get(name);if(!h)continue;nowState.heroes[name]={wr:Number.isFinite(h.wr)?h.wr:null,ban:Number.isFinite(h.ban)?h.ban:null,pick:Number.isFinite(h.pick)?h.pick:null,rankWr:ranks.wr.get(name)||null,rankBan:ranks.ban.get(name)||null,rankPick:ranks.pick.get(name)||null}}
if(!previous||!previous.heroes){localStorage.setItem(SEEN,JSON.stringify(nowState));return}
if(previous.snapshot===snapshotId)return;
const alerts=[];
const addRank=(name,label,a,b)=>{
 if(!Number.isFinite(a)||!Number.isFinite(b))return;
 if(a<=10&&b>10){alerts.push({name,type:'rank',weight:10+(11-a)/10,text:`Entró al Top 10 ${label} (#${a})`});return}
 const jump=b-a;
 if(jump>=10)alerts.push({name,type:'rank',weight:5+Math.min(jump,30)/10,text:`Subió ${jump} puestos en ${label} (#${a})`});
};
for(const name of watched){const a=nowState.heroes[name],b=previous.heroes?.[name];if(!a||!b)continue;
 if(Number.isFinite(a.wr)&&Number.isFinite(b.wr)){const d=a.wr-b.wr;if(Math.abs(d)>=0.35)alerts.push({name,type:d>0?'up':'down',weight:Math.abs(d),text:`${d>0?'+':''}${d.toFixed(2)} pp WR`})}
 if(Number.isFinite(a.ban)&&Number.isFinite(b.ban)){const d=a.ban-b.ban;if(Math.abs(d)>=3)alerts.push({name,type:'ban',weight:Math.abs(d)/3,text:`${d>0?'+':''}${d.toFixed(2)} pp ban`})}
 if(Number.isFinite(a.pick)&&Number.isFinite(b.pick)){const d=a.pick-b.pick;if(Math.abs(d)>=3)alerts.push({name,type:'pick',weight:Math.abs(d)/3,text:`${d>0?'+':''}${d.toFixed(2)} pp pick`})}
 addRank(name,'WR',a.rankWr,b.rankWr);addRank(name,'ban',a.rankBan,b.rankBan);addRank(name,'pick',a.rankPick,b.rankPick);
}
const dedup=[];const seen=new Set();
for(const x of alerts.sort((a,b)=>b.weight-a.weight)){const key=x.name+'|'+x.text;if(seen.has(key))continue;seen.add(key);dedup.push(x)}
const top=dedup.slice(0,10);
if(top.length){panel.hidden=false;count.textContent=String(top.length);period.textContent=`${previous.updated||'última visita'} → ${cur.updated||'snapshot actual'} · ${cur.patch||'patch sin dato'}`;list.innerHTML=top.map(x=>`<div class="pulse-item"><b>${x.name}</b><span class="pulse-${x.type}">${x.text}</span></div>`).join('')}
localStorage.setItem(SEEN,JSON.stringify(nowState));
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Injected Watchlist Pulse with WR, ban and pick ranking alerts')
