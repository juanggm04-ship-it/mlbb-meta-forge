from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="draftTimeline"' in html:
    print('Turn draft styling already injected')
    raise SystemExit

css='''<style>
.turn-draft{position:relative;overflow:hidden;background:linear-gradient(110deg,#071325 0%,#0d1320 47%,#17101a 53%,#210e14 100%);box-shadow:0 24px 70px #0008}
.turn-draft:before,.turn-draft:after{content:'';position:absolute;top:0;bottom:0;width:34%;pointer-events:none;opacity:.22}.turn-draft:before{left:0;background:radial-gradient(circle at left,#2b8cff55,transparent 68%)}.turn-draft:after{right:0;background:radial-gradient(circle at right,#ff4b6e55,transparent 68%)}
.turn-head,.turn-board,.turn-pool,.turn-actions,.turn-recs,.draft-timeline{position:relative;z-index:1}.turn-team{position:relative;overflow:hidden}.turn-team:first-child{border-color:#2a66a8;background:linear-gradient(145deg,#0a1628,#0b111b)}.turn-team:last-child{border-color:#8a3041;background:linear-gradient(145deg,#1a0d14,#0d1119)}.turn-team:first-child h4{color:#70b7ff}.turn-team:last-child h4{color:#ff8298}.turn-slot{min-height:54px;gap:12px}.turn-slot b{display:flex;align-items:center;gap:10px}.td-avatar{width:34px;height:34px;border-radius:10px;overflow:hidden;background:#15233a;border:1px solid #ffffff18;flex:0 0 auto}.td-avatar img{width:100%;height:100%;object-fit:cover;display:block}.td-fallback{width:100%;height:100%;display:grid;place-items:center;font-size:10px;font-weight:900;color:#8fa4c5}.turn-highlight{margin-top:12px;padding:14px 16px;border-radius:16px;border:1px solid #ffcf5755;background:linear-gradient(135deg,#261f0d,#15121d)}.turn-highlight small{display:block;color:#e6b947;font-size:9px;letter-spacing:.12em;font-weight:900}.turn-highlight strong{display:block;font-size:20px;margin-top:4px}.turn-highlight span{display:block;color:#9eabc0;font-size:12px;margin-top:5px}.draft-timeline{margin:16px 0;padding:14px;border:1px solid #2b3953;border-radius:16px;background:#09101bcc}.timeline-row{display:flex;gap:6px;overflow:auto;padding-bottom:3px}.timeline-step{flex:0 0 auto;min-width:72px;padding:8px 9px;border-radius:10px;background:#111a2a;border:1px solid #273751;color:#70809c;font-size:9px;text-align:center;font-weight:900}.timeline-step.done{color:#dbe8f8;border-color:#415775}.timeline-step.current{color:#07101a;background:#ffcf57;border-color:#ffcf57;box-shadow:0 0 24px #ffcf5738}.timeline-step.blue.done{box-shadow:inset 0 2px 0 #4aa5ff}.timeline-step.red.done{box-shadow:inset 0 2px 0 #ff607c}.turn-hero{display:inline-flex;align-items:center;gap:7px}.turn-hero .mini-avatar{width:23px;height:23px;border-radius:7px;overflow:hidden;background:#18253b}.turn-hero .mini-avatar img{width:100%;height:100%;object-fit:cover}.turn-rec.primary-rec{border-color:#ffcf5788;background:#ffcf5711;color:#ffe39a;font-weight:900;box-shadow:0 0 20px #ffcf5714}.turn-status{font-size:14px;letter-spacing:.04em}.turn-side button.active{box-shadow:0 0 22px #46e6ff28}
</style>'''
html=html.replace('</head>',css+'</head>')

needle='<div id="turnStatus" class="turn-status">Preparando draft…</div>'
addon='''<div id="turnStatus" class="turn-status">Preparando draft…</div><div id="draftTimeline" class="draft-timeline"><div id="timelineRow" class="timeline-row"></div></div><div id="turnHighlight" class="turn-highlight"><small>RECOMENDACIÓN PRINCIPAL</small><strong>Esperando turno</strong><span>La sugerencia cambia con cada pick y ban.</span></div>'''
if needle not in html:
    raise RuntimeError('Turn status not found')
html=html.replace(needle,addon)

js=r'''<script>
(()=>{
const root=document.getElementById('turnDraft'); if(!root)return;
const timeline=document.getElementById('timelineRow');
const highlight=document.getElementById('turnHighlight');
function imgFor(name){const h=DATA.heroes.find(x=>x.name===name);if(!h)return'';return `https://raw.githubusercontent.com/Ceplin03/database-mlbb.Mobile-Legends-Bang-Bang/master/images-hero/${h.asset}`}
function enhanceSlots(){
 document.querySelectorAll('#blueSlots .turn-slot b,#redSlots .turn-slot b').forEach(b=>{
   const name=b.textContent.trim(); if(!name||name==='—'||b.querySelector('.td-avatar'))return;
   b.textContent=''; const av=document.createElement('span');av.className='td-avatar';av.innerHTML=`<span class="td-fallback">${name.slice(0,2).toUpperCase()}</span><img src="${imgFor(name)}" alt="" onerror="this.style.display='none'">`;b.append(av,document.createTextNode(name));
 });
}
function enhancePool(){
 document.querySelectorAll('#turnHeroes .turn-hero').forEach(btn=>{if(btn.querySelector('.mini-avatar'))return;const n=btn.dataset.hero;const av=document.createElement('span');av.className='mini-avatar';av.innerHTML=`<img src="${imgFor(n)}" alt="" onerror="this.style.display='none'">`;btn.prepend(av)});
}
function buildTimeline(){
 const statusText=document.getElementById('turnStatus').textContent;
 const seq=[]; ['BAN 1','BAN 2','BAN 3','PICK 1','PICK 2','PICK 3','BAN 4','BAN 5','PICK 4','PICK 5'].forEach(x=>{seq.push(['BLUE',x]);seq.push(['RED',x])});
 timeline.innerHTML=seq.map(([s,t])=>`<div class="timeline-step ${s.toLowerCase()}">${s[0]} · ${t}</div>`).join('');
 const steps=[...timeline.children]; let currentIndex=steps.findIndex(el=>statusText.startsWith(el.textContent.replace('B ·','BLUE ·').replace('R ·','RED ·')));
 if(currentIndex<0){const normalized=statusText.replace('BLUE','B').replace('RED','R');currentIndex=steps.findIndex(el=>normalized.startsWith(el.textContent))}
 if(currentIndex<0&&statusText.includes('Draft completo'))currentIndex=steps.length;
 steps.forEach((el,i)=>{el.classList.toggle('done',i<currentIndex);el.classList.toggle('current',i===currentIndex)});
 if(currentIndex>=0&&currentIndex<steps.length)steps[currentIndex].scrollIntoView({behavior:'smooth',block:'nearest',inline:'center'});
}
function highlightRec(){
 const recs=[...document.querySelectorAll('#turnRecs .turn-rec')];recs.forEach((x,i)=>x.classList.toggle('primary-rec',i===0));
 const first=recs[0];
 if(first&&first.textContent.trim()!=='Draft completo'){
   const side=document.getElementById('turnStatus').textContent.startsWith('RED')?'Red':'Blue';
   highlight.innerHTML=`<small>RECOMENDACIÓN PRINCIPAL · ${side}</small><strong>${first.textContent.trim()}</strong><span>Mejor encaje editorial disponible para el turno actual dentro del pool rastreado.</span>`;
 }else if(document.getElementById('turnStatus').textContent.includes('Draft completo')){
   highlight.innerHTML='<small>DRAFT COMPLETO</small><strong>Secuencia terminada</strong><span>Revisa composición, matchups y estructura antes de reiniciar.</span>';
 }
}
const observer=new MutationObserver(()=>{enhanceSlots();enhancePool();buildTimeline();highlightRec()});
observer.observe(root,{childList:true,subtree:true,characterData:true});
setTimeout(()=>{enhanceSlots();enhancePool();buildTimeline();highlightRec()},50);
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Styled turn draft with portraits, timeline and highlighted recommendation')
