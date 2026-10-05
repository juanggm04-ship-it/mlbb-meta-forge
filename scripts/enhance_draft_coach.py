from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="coachMatchups"' in html:
    print('Draft Coach enhancements already injected')
    raise SystemExit

extra_css='''<style>
.coach-chip{cursor:pointer;transition:.18s transform,.18s border-color,.18s background}.coach-chip:hover{transform:translateY(-2px);border-color:#46e6ff88;background:#132238}.coach-chip:focus-visible{outline:3px solid #46e6ff;outline-offset:2px}.coach-chip.is-disabled{opacity:.45;cursor:not-allowed;transform:none}.coach-matchups{margin-top:16px;padding-top:14px;border-top:1px solid #22304b}.coach-matchups h5{margin:0 0 10px;font-size:13px;color:#cdd8ea}.match-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.match-card{padding:11px 12px;border:1px solid #293956;border-radius:12px;background:#0a111e}.match-card b{display:block;font-size:12px}.match-card span{display:block;margin-top:4px;color:#8392ad;font-size:11px;line-height:1.45}.match-card.good{border-color:#2f6b58}.match-card.warn{border-color:#71582e}.coach-hint{display:block;margin-top:8px;color:#6f809d;font-size:10px}@media(max-width:700px){.match-grid{grid-template-columns:1fr}}
</style>'''
html=html.replace('</head>',extra_css+'</head>')

marker='<div id="coachRecs"></div></div></div></div><p class="coach-note">'
replacement='<div id="coachRecs"></div><small class="coach-hint">Haz clic en una recomendación para añadirla al primer espacio libre de tu equipo.</small></div><div id="coachMatchups" class="coach-matchups"><h5>Matchups editoriales detectados</h5><div id="coachMatchupGrid" class="match-grid"></div></div></div></div><p class="coach-note">'
if marker not in html:
    raise RuntimeError('Coach recommendation block not found')
html=html.replace(marker,replacement)

extra_js=r'''<script>
(()=>{
const root=document.getElementById('draftCoach');
if(!root)return;
const selects=[...root.querySelectorAll('select')];
const recBox=document.getElementById('coachRecs');
const matchGrid=document.getElementById('coachMatchupGrid');

const MATCH={
'Hayabusa':{warn:['Valir','Khufra','Diggie','Belerick'],good:['Eudora','Pharsa','Ixia','Bruno']},
'Nolan':{warn:['Valir','Khufra','Diggie','Belerick'],good:['Eudora','Pharsa','Ixia','Bruno']},
'Hirara':{warn:['Khufra','Valir','Minotaur','Belerick'],good:['Eudora','Pharsa','Ixia','Bruno']},
'Aulus':{warn:['Valir','Gloo','Belerick'],good:['Rafaela','Minotaur','Xavier']},
'Masha':{warn:['Valir','Gloo','Ruby'],good:['Ixia','Bruno','Eudora']},
'Estes':{warn:['Valir','Eudora'],good:['Fredrinn','Ruby','Masha']},
'Rafaela':{warn:['Eudora','Hayabusa','Nolan'],good:['Aulus','Ixia','Bruno']},
'Obsidia':{warn:['Hayabusa','Nolan','Hirara'],good:['Minotaur','Lolita','Rafaela']},
'Bruno':{warn:['Hayabusa','Nolan','Hirara'],good:['Minotaur','Lolita','Rafaela']},
'Ixia':{warn:['Hayabusa','Nolan','Hirara'],good:['Minotaur','Lolita','Tigreal']},
'Valir':{warn:['Hayabusa','Nolan','Masha'],good:['Khufra','Minotaur','Tigreal']},
'Eudora':{warn:['Masha','Gloo','Ruby'],good:['Khufra','Tigreal','Minotaur']}
};

function values(prefix){return [0,1,2,3,4].map(i=>document.getElementById(prefix+i)?.value).filter(Boolean)}
function updateLocks(){
  const chosen=selects.map(s=>s.value).filter(Boolean);
  selects.forEach(s=>{
    [...s.options].forEach(o=>{
      if(!o.value){o.disabled=false;return}
      o.disabled=chosen.includes(o.value)&&s.value!==o.value;
    });
  });
}
function matchupText(a,e){
  const aRule=MATCH[a]||{};
  const eRule=MATCH[e]||{};
  if((aRule.good||[]).includes(e)) return ['good',`${a} puede castigar a ${e}`,'Lectura editorial por acceso, rango o patrón de pelea.'];
  if((aRule.warn||[]).includes(e)) return ['warn',`${a} debe respetar a ${e}`,'El rival tiene herramientas editoriales que pueden limitar su plan de juego.'];
  if((eRule.good||[]).includes(a)) return ['warn',`${e} puede castigar a ${a}`,'El rival tiene una interacción de draft favorable según nuestras etiquetas.'];
  if((eRule.warn||[]).includes(a)) return ['good',`${a} responde bien a ${e}`,'Tu pick aporta herramientas útiles contra el patrón del rival.'];
  return null;
}
function renderMatchups(){
  const A=values('a'),E=values('e'),items=[];
  for(const a of A){for(const e of E){const m=matchupText(a,e);if(m)items.push(m)}}
  const unique=[]; const seen=new Set();
  for(const m of items){const k=m[1];if(!seen.has(k)){seen.add(k);unique.push(m)} if(unique.length>=6)break}
  matchGrid.innerHTML=unique.length?unique.map(m=>`<div class="match-card ${m[0]}"><b>${m[1]}</b><span>${m[2]}</span></div>`).join(''):'<div class="match-card"><b>Sin choque editorial destacado</b><span>Añade picks de ambos equipos para detectar interacciones del pool actual.</span></div>';
}
function enhanceRecButtons(){
  [...recBox.querySelectorAll('.coach-chip')].forEach(chip=>{
    if(chip.dataset.enhanced)return;
    chip.dataset.enhanced='1';
    chip.setAttribute('role','button'); chip.setAttribute('tabindex','0');
    const activate=()=>{
      const name=chip.textContent.trim();
      if(!name||name.includes('Añade picks'))return;
      const chosen=selects.map(s=>s.value).filter(Boolean);
      if(chosen.includes(name)){chip.classList.add('is-disabled');return}
      const empty=[0,1,2,3,4].map(i=>document.getElementById('a'+i)).find(s=>s&&!s.value);
      if(!empty)return;
      empty.value=name; empty.dispatchEvent(new Event('change',{bubbles:true}));
    };
    chip.addEventListener('click',activate);
    chip.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate()}});
  });
}

selects.forEach(s=>s.addEventListener('change',()=>{updateLocks();renderMatchups();setTimeout(enhanceRecButtons,0)}));
const observer=new MutationObserver(()=>enhanceRecButtons());
observer.observe(recBox,{childList:true,subtree:true});
updateLocks();renderMatchups();enhanceRecButtons();
})();
</script>'''
html=html.replace('</body>',extra_js+'</body>')
p.write_text(html,encoding='utf-8')
print('Enhanced Draft Coach with locks, clickable recommendations and editorial matchups')
