from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="turnDraft"' in html:
    print('Turn Draft already injected')
    raise SystemExit

css='''<style>
.turn-draft{margin-top:20px;padding:24px;border:1px solid #2b3a58;border-radius:24px;background:linear-gradient(145deg,#0b1322,#151229)}
.turn-head{display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap}.turn-head h3{margin:5px 0;font-size:28px}.turn-side{display:flex;gap:8px}.turn-side button{border:1px solid #30415f;background:#10192b;color:#b7c4da;border-radius:11px;padding:9px 12px;cursor:pointer}.turn-side button.active{background:#46e6ff;color:#06101a;border-color:#46e6ff}.turn-status{margin:16px 0;padding:12px 14px;border-radius:14px;background:#08101c;border:1px solid #243450;color:#dbe6f8;font-weight:800}.turn-board{display:grid;grid-template-columns:1fr 1fr;gap:14px}.turn-team{padding:16px;border-radius:18px;background:#0a101c;border:1px solid #22304b}.turn-team h4{margin:0 0 12px}.turn-slots{display:grid;gap:8px}.turn-slot{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border-radius:12px;background:#0e1727;border:1px solid #263653}.turn-slot span{font-size:11px;color:#7f90ad}.turn-slot b{font-size:13px}.turn-pool{margin-top:16px}.turn-pool input{width:100%;background:#0b1321;border:1px solid #2a3956;color:#edf4ff;border-radius:12px;padding:11px 13px}.turn-heroes{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px;max-height:230px;overflow:auto}.turn-hero{border:1px solid #2d3e5b;background:#10192a;color:#dce7f9;border-radius:999px;padding:8px 10px;cursor:pointer;font-size:12px}.turn-hero:hover{border-color:#46e6ff88}.turn-hero:disabled{opacity:.35;cursor:not-allowed}.turn-actions{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}.turn-actions button{border:1px solid #334461;background:#111a2c;color:#d9e4f5;border-radius:11px;padding:9px 12px;cursor:pointer}.turn-recs{margin-top:16px;padding-top:14px;border-top:1px solid #24324c}.turn-recs strong{font-size:13px}.turn-rec{display:inline-flex;margin:6px 6px 0 0;padding:8px 10px;border:1px solid #2e3e5a;border-radius:999px;background:#111a2a;color:#cbd7eb;font-size:12px;cursor:pointer}.turn-rec:hover{border-color:#46e6ff88}.turn-note{color:#71809b;font-size:11px;line-height:1.55;margin-top:12px}@media(max-width:760px){.turn-board{grid-template-columns:1fr}}
</style>'''
html=html.replace('</head>',css+'</head>')

markup='''<div id="turnDraft" class="turn-draft"><div class="turn-head"><div><small>DRAFT POR TURNOS</small><h3>Blue vs Red</h3></div><div class="turn-side"><button id="blueFirst" class="active" type="button">Blue first</button><button id="redFirst" type="button">Red first</button></div></div><div id="turnStatus" class="turn-status">Preparando draft…</div><div class="turn-board"><section class="turn-team"><h4>Blue</h4><div id="blueSlots" class="turn-slots"></div></section><section class="turn-team"><h4>Red</h4><div id="redSlots" class="turn-slots"></div></section></div><div class="turn-pool"><input id="turnSearch" type="search" placeholder="Buscar héroe para el turno actual…"><div id="turnHeroes" class="turn-heroes"></div></div><div class="turn-actions"><button id="turnUndo" type="button">↶ Deshacer</button><button id="turnReset" type="button">Limpiar draft</button></div><div class="turn-recs"><strong>Recomendaciones para el turno actual</strong><div id="turnRecs"></div></div><p class="turn-note">Secuencia simplificada de draft competitivo para entrenamiento. Picks y bans usados quedan bloqueados. Las recomendaciones son editoriales, no predicciones de victoria.</p></div>'''
needle='<div id="draftCoach" class="coach-wrap">'
if needle not in html:
    raise RuntimeError('Draft Coach not found')
html=html.replace(needle,markup+needle)

js=r'''<script>
(()=>{
const root=document.getElementById('turnDraft'); if(!root)return;
const blueSlots=document.getElementById('blueSlots'),redSlots=document.getElementById('redSlots'),pool=document.getElementById('turnHeroes'),status=document.getElementById('turnStatus'),search=document.getElementById('turnSearch'),recs=document.getElementById('turnRecs');
let first='blue',history=[];
const baseBlue=['B BAN 1','B BAN 2','B BAN 3','B1','B2','B3','B BAN 4','B BAN 5','B4','B5'];
const baseRed=['R BAN 1','R BAN 2','R BAN 3','R1','R2','R3','R BAN 4','R BAN 5','R4','R5'];
function seq(){
 const blueFirst=[['blue','ban',1],['red','ban',1],['blue','ban',2],['red','ban',2],['blue','ban',3],['red','ban',3],['blue','pick',1],['red','pick',1],['red','pick',2],['blue','pick',2],['blue','pick',3],['red','pick',3],['red','ban',4],['blue','ban',4],['red','ban',5],['blue','ban',5],['red','pick',4],['red','pick',5],['blue','pick',4],['blue','pick',5]];
 if(first==='blue')return blueFirst;
 return blueFirst.map(x=>[x[0]==='blue'?'red':'blue',x[1],x[2]]);
}
function used(){return new Set(history.map(x=>x.hero))}
function teamPicks(side){return history.filter(x=>x.side===side&&x.type==='pick').map(x=>x.hero)}
function teamBans(side){return history.filter(x=>x.side===side&&x.type==='ban').map(x=>x.hero)}
function profileScore(hero,side){const mine=teamPicks(side),enemy=teamPicks(side==='blue'?'red':'blue'),h=DATA.heroes.find(x=>x.name===hero);let s=(h?.tier==='S+'?5:2)+(h?.wr||50)/20;const lanes=new Set(mine.map(n=>DATA.heroes.find(h=>h.name===n)?.lane));if(h&&!lanes.has(h.lane))s+=3;if(enemy.includes('Hayabusa')||enemy.includes('Nolan')||enemy.includes('Hirara')){if(['Khufra','Minotaur','Valir','Lolita','Belerick'].includes(hero))s+=4}if(mine.includes('Ixia')||mine.includes('Bruno')||mine.includes('Obsidia')){if(['Rafaela','Minotaur','Lolita','Tigreal'].includes(hero))s+=3}return s}
function current(){return seq()[history.length]}
function choose(hero){const c=current();if(!c||used().has(hero))return;history.push({side:c[0],type:c[1],slot:c[2],hero});render()}
function slotText(side,type,n){const x=history.find(h=>h.side===side&&h.type===type&&h.slot===n);return x?.hero||'—'}
function renderTeam(el,side){let out='';for(let i=1;i<=3;i++)out+=`<div class="turn-slot"><span>BAN ${i}</span><b>${slotText(side,'ban',i)}</b></div>`;for(let i=1;i<=3;i++)out+=`<div class="turn-slot"><span>PICK ${i}</span><b>${slotText(side,'pick',i)}</b></div>`;for(let i=4;i<=5;i++)out+=`<div class="turn-slot"><span>BAN ${i}</span><b>${slotText(side,'ban',i)}</b></div>`;for(let i=4;i<=5;i++)out+=`<div class="turn-slot"><span>PICK ${i}</span><b>${slotText(side,'pick',i)}</b></div>`;el.innerHTML=out}
function renderPool(){const q=search.value.toLowerCase(),u=used();pool.innerHTML=DATA.heroes.filter(h=>h.name.toLowerCase().includes(q)).map(h=>`<button class="turn-hero" ${u.has(h.name)?'disabled':''} data-hero="${h.name.replace(/"/g,'&quot;')}">${h.name}</button>`).join('');pool.querySelectorAll('.turn-hero').forEach(b=>b.onclick=()=>choose(b.dataset.hero))}
function renderRecs(){const c=current();if(!c){recs.innerHTML='<span class="turn-rec">Draft completo</span>';return}const side=c[0],u=used();let arr=DATA.heroes.filter(h=>!u.has(h.name));if(c[1]==='pick')arr.sort((a,b)=>profileScore(b.name,side)-profileScore(a.name,side));else arr.sort((a,b)=>(b.ban||0)-(a.ban||0));arr=arr.slice(0,5);recs.innerHTML=arr.map(h=>`<button class="turn-rec" data-hero="${h.name}">${h.name}</button>`).join('');recs.querySelectorAll('.turn-rec').forEach(b=>b.onclick=()=>choose(b.dataset.hero))}
function render(){renderTeam(blueSlots,'blue');renderTeam(redSlots,'red');renderPool();renderRecs();const c=current();status.textContent=c?`${c[0]==='blue'?'BLUE':'RED'} · ${c[1]==='ban'?'BAN':'PICK'} ${c[2]}`:'Draft completo. Puedes revisar el resultado o reiniciar.';document.getElementById('blueFirst').classList.toggle('active',first==='blue');document.getElementById('redFirst').classList.toggle('active',first==='red')}
search.oninput=renderPool;document.getElementById('turnUndo').onclick=()=>{history.pop();render()};document.getElementById('turnReset').onclick=()=>{history=[];render()};document.getElementById('blueFirst').onclick=()=>{first='blue';history=[];render()};document.getElementById('redFirst').onclick=()=>{first='red';history=[];render()};render();
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Injected turn-based draft mode')
