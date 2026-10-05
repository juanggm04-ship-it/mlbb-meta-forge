from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="saveTurnDraft"' in html:
    print('Turn draft sharing already injected')
    raise SystemExit

css='''<style>
.turn-sharebar{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;padding-top:12px;border-top:1px solid #263652}.turn-sharebar button{border:1px solid #334461;background:#111a2c;color:#dce7f7;border-radius:11px;padding:9px 12px;cursor:pointer}.turn-sharebar button:hover{border-color:#46e6ff88}.turn-saved{margin-top:12px;display:grid;gap:8px}.turn-saved-item{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:10px 12px;border:1px solid #283853;border-radius:12px;background:#0b1321}.turn-saved-item small{color:#7f8eaa}.turn-saved-actions{display:flex;gap:6px}.turn-saved-actions button{padding:7px 9px;border-radius:9px}.turn-share-note{margin-top:8px;color:#71809b;font-size:10px;line-height:1.45}
</style>'''
html=html.replace('</head>',css+'</head>')

bar='''<div class="turn-sharebar"><button id="saveTurnDraft" type="button">Guardar draft competitivo</button><button id="shareTurnDraft" type="button">Compartir draft competitivo</button></div><div id="turnSavedDrafts" class="turn-saved"></div><p class="turn-share-note">Guarda first pick, bans, picks y orden completo en este dispositivo. El enlace compartible reconstruye la simulación en el navegador.</p>'''
needle='<div class="turn-actions"><button id="turnUndo" type="button">↶ Deshacer</button><button id="turnReset" type="button">Limpiar draft</button></div>'
if needle not in html:
    raise RuntimeError('Turn draft actions not found')
html=html.replace(needle,needle+bar)

js=r'''<script>
(()=>{
const STORE='mf_turn_draft_history_v1';
const blue=document.getElementById('blueSlots'), red=document.getElementById('redSlots');
if(!blue||!red)return;
const sequence=(first)=>{
 const b=[['blue','ban',1],['red','ban',1],['blue','ban',2],['red','ban',2],['blue','ban',3],['red','ban',3],['blue','pick',1],['red','pick',1],['red','pick',2],['blue','pick',2],['blue','pick',3],['red','pick',3],['red','ban',4],['blue','ban',4],['red','ban',5],['blue','ban',5],['red','pick',4],['red','pick',5],['blue','pick',4],['blue','pick',5]];
 return first==='blue'?b:b.map(x=>[x[0]==='blue'?'red':'blue',x[1],x[2]]);
};
function readTeam(side){
 const root=side==='blue'?blue:red, map={ban:{},pick:{}};
 [...root.querySelectorAll('.turn-slot')].forEach(slot=>{
   const label=slot.querySelector('span')?.textContent.trim()||'';
   const hero=slot.querySelector('b')?.textContent.trim()||'—';
   const m=label.match(/^(BAN|PICK)\s+(\d)$/);
   if(m&&hero&&hero!=='—')map[m[1].toLowerCase()][+m[2]]=hero;
 });
 return map;
}
function snapshot(){
 const first=document.getElementById('redFirst')?.classList.contains('active')?'red':'blue';
 const B=readTeam('blue'),R=readTeam('red');
 const hist=[];
 for(const [side,type,slot] of sequence(first)){
   const src=side==='blue'?B:R, hero=src[type][slot];
   if(hero)hist.push({side,type,slot,hero}); else break;
 }
 return {first,history:hist,ts:Date.now(),patch:DATA?.patch||''};
}
function loadSaved(){try{return JSON.parse(localStorage.getItem(STORE)||'[]')}catch{return []}}
function writeSaved(x){localStorage.setItem(STORE,JSON.stringify(x.slice(0,8)))}
function encode(obj){return btoa(unescape(encodeURIComponent(JSON.stringify({f:obj.first,h:obj.history.map(x=>x.hero)})))).replace(/=+$/,'').replace(/\+/g,'-').replace(/\//g,'_')}
function decode(s){try{const raw=s.replace(/-/g,'+').replace(/_/g,'/');const pad=raw+'==='.slice((raw.length+3)%4);return JSON.parse(decodeURIComponent(escape(atob(pad))))}catch{return null}}
function renderSaved(){
 const box=document.getElementById('turnSavedDrafts'); if(!box)return;
 const arr=loadSaved();
 box.innerHTML=arr.length?arr.map((d,i)=>`<div class="turn-saved-item"><div><b>${d.first==='red'?'Red':'Blue'} first · ${d.history.length}/20 pasos</b><small> · ${new Date(d.ts).toLocaleString()}</small></div><div class="turn-saved-actions"><button data-turn-load="${i}">Cargar</button><button data-turn-share="${i}">Enlace</button></div></div>`).join(''):'';
 box.querySelectorAll('[data-turn-load]').forEach(b=>b.onclick=()=>restore(arr[+b.dataset.turnLoad]));
 box.querySelectorAll('[data-turn-share]').forEach(b=>b.onclick=()=>copyLink(arr[+b.dataset.turnShare]));
}
function findHeroButton(hero){return [...document.querySelectorAll('#turnHeroes .turn-hero')].find(b=>b.dataset.hero===hero&&!b.disabled)}
function restore(d){
 const first=d.first==='red'?'red':'blue';
 document.getElementById(first==='red'?'redFirst':'blueFirst')?.click();
 document.getElementById('turnReset')?.click();
 let i=0;
 const heroes=(d.history||[]).map(x=>typeof x==='string'?x:x.hero);
 const step=()=>{
   if(i>=heroes.length)return;
   const hero=heroes[i++];
   const btn=findHeroButton(hero);
   if(btn){btn.click();setTimeout(step,0)}
 };
 setTimeout(step,0);
 document.querySelector('.tab[data-view="drafts"]')?.click();
 setTimeout(()=>document.getElementById('turnDraft')?.scrollIntoView({behavior:'smooth',block:'start'}),120);
}
async function copyLink(d){
 const url=new URL(location.href);url.searchParams.delete('draft');url.searchParams.set('turnDraft',encode(d));
 try{await navigator.clipboard.writeText(url.toString());alert('Enlace del draft competitivo copiado.')}catch{prompt('Copia este enlace:',url.toString())}
}
document.getElementById('saveTurnDraft')?.addEventListener('click',()=>{const d=snapshot();const arr=loadSaved();arr.unshift(d);writeSaved(arr);renderSaved()});
document.getElementById('shareTurnDraft')?.addEventListener('click',()=>copyLink(snapshot()));
const param=new URL(location.href).searchParams.get('turnDraft');
if(param){const d=decode(param);if(d&&['blue','red'].includes(d.f)&&Array.isArray(d.h)){const hist=sequence(d.f).slice(0,d.h.length).map((x,i)=>({side:x[0],type:x[1],slot:x[2],hero:d.h[i]}));setTimeout(()=>restore({first:d.f,history:hist}),650)}}
renderSaved();
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Added save/share/restore for full turn-based drafts')
