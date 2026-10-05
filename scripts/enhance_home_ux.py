from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="homeQuickActions"' in html:
    print('Home UX already enhanced')
    raise SystemExit

css='''<style>
.quick-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:18px 0 0}.quick-action{border:1px solid #2a3a59;background:linear-gradient(145deg,#0d1626,#111a2c);border-radius:16px;padding:15px;text-align:left;color:#eaf2ff;cursor:pointer}.quick-action b{display:block;font-size:14px}.quick-action span{display:block;margin-top:4px;color:#7f90ad;font-size:11px;line-height:1.4}.draft-library{margin-top:18px;padding:18px;border:1px solid #263652;border-radius:18px;background:#0a111f}.draft-library-head{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}.draft-library h4{margin:0}.draft-library-actions{display:flex;gap:8px;flex-wrap:wrap}.draft-library-actions button{border:1px solid #33435f;background:#111a2c;color:#dbe6f7;border-radius:10px;padding:9px 11px;cursor:pointer}.draft-history{display:grid;gap:8px;margin-top:12px}.draft-history-item{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:10px 12px;border:1px solid #263650;border-radius:12px;background:#0c1423}.draft-history-item span{color:#8796b1;font-size:11px}.draft-history-item button{border:1px solid #30425f;background:#121d31;color:#dbe7f8;border-radius:9px;padding:7px 9px;cursor:pointer}.mobile-dock{display:none}@media(max-width:760px){.quick-actions{grid-template-columns:1fr}.mobile-dock{position:fixed;left:12px;right:12px;bottom:12px;z-index:45;display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:6px;background:#0a101ddd;border:1px solid #2b3956;border-radius:16px;backdrop-filter:blur(14px);box-shadow:0 18px 50px #0009}.mobile-dock button{border:0;background:#111a2c;color:#dbe7f8;border-radius:11px;padding:10px 6px;font-size:11px;font-weight:800}.mobile-dock button.active{background:#46e6ff;color:#061019}body{padding-bottom:78px}}
</style>'''
html=html.replace('</head>',css+'</head>')

quick='''<div id="homeQuickActions" class="quick-actions"><button class="quick-action" type="button" data-go="drafts"><b>⚔ Abrir Draft Lab</b><span>Coach, 5v5 libre y modo Blue vs Red.</span></button><button class="quick-action" type="button" id="quickHeroes"><b>⌕ Explorar héroes</b><span>Buscar por rol, tier, win rate y ban rate.</span></button><button class="quick-action" type="button" id="quickSaved"><b>▣ Mis drafts</b><span>Guarda composiciones recientes en este dispositivo.</span></button></div>'''
needle='<div class="hero-actions">'
if needle in html:
    idx=html.find('</div><div class="hero-kpis">',html.find(needle))
    if idx!=-1:
        html=html[:idx+6]+quick+html[idx+6:]

library='''<div id="draftLibrary" class="draft-library"><div class="draft-library-head"><h4>Mis drafts</h4><div class="draft-library-actions"><button id="saveFreeDraft" type="button">Guardar draft libre</button><button id="shareFreeDraft" type="button">Compartir draft libre</button></div></div><div id="draftHistory" class="draft-history"></div><p class="coach-note">Los drafts se guardan solo en tu navegador. Los enlaces compartibles codifican la selección en la URL y no requieren cuenta.</p></div>'''
needle2='<p class="coach-note">El análisis usa etiquetas editoriales del pool actual, no probabilidades de victoria ni datos oficiales de counter.</p></div>'
if needle2 in html:
    html=html.replace(needle2,needle2+library)

mobile='''<div class="mobile-dock" id="mobileDock"><button data-view-target="heroes">Meta</button><button data-view-target="drafts">Draft</button><button data-view-target="tips">Tips</button></div>'''
html=html.replace('</body>',mobile+'</body>')

js=r'''<script>
(()=>{
const STORAGE='mf_draft_history_v1';
function activateView(id){const tab=document.querySelector(`.tab[data-view="${id}"]`);if(tab)tab.click();setTimeout(()=>document.getElementById(id)?.scrollIntoView({behavior:'smooth',block:'start'}),30)}
document.querySelectorAll('[data-go="drafts"]').forEach(b=>b.onclick=()=>activateView('drafts'));
document.getElementById('quickHeroes')?.addEventListener('click',()=>{activateView('heroes');setTimeout(()=>document.getElementById('heroSearch')?.focus(),250)});
document.getElementById('quickSaved')?.addEventListener('click',()=>{activateView('drafts');setTimeout(()=>document.getElementById('draftLibrary')?.scrollIntoView({behavior:'smooth'}),200)});
document.querySelectorAll('#mobileDock [data-view-target]').forEach(b=>b.addEventListener('click',()=>activateView(b.dataset.viewTarget)));
function syncDock(){const active=document.querySelector('.tab.active')?.dataset.view;document.querySelectorAll('#mobileDock button').forEach(b=>b.classList.toggle('active',b.dataset.viewTarget===active))}
document.querySelectorAll('.tab').forEach(t=>t.addEventListener('click',syncDock));syncDock();
function freeDraft(){const allies=[0,1,2,3,4].map(i=>document.getElementById('a'+i)?.value).filter(Boolean);const enemies=[0,1,2,3,4].map(i=>document.getElementById('e'+i)?.value).filter(Boolean);return {allies,enemies,ts:Date.now()}}
function loadHistory(){try{return JSON.parse(localStorage.getItem(STORAGE)||'[]')}catch{return []}}
function writeHistory(items){localStorage.setItem(STORAGE,JSON.stringify(items.slice(0,8)))}
function renderHistory(){const box=document.getElementById('draftHistory');if(!box)return;const items=loadHistory();box.innerHTML=items.length?items.map((d,i)=>`<div class="draft-history-item"><div><b>${d.allies.join(', ')||'Sin aliados'}</b><span> vs ${d.enemies.join(', ')||'Sin rivales'}</span></div><button data-load="${i}">Cargar</button></div>`).join(''):'<div class="draft-history-item"><span>Aún no has guardado drafts.</span></div>';box.querySelectorAll('[data-load]').forEach(b=>b.onclick=()=>restore(items[+b.dataset.load]))}
function restore(d){[0,1,2,3,4].forEach((i)=>{const a=document.getElementById('a'+i),e=document.getElementById('e'+i);if(a){a.value=d.allies[i]||'';a.dispatchEvent(new Event('change',{bubbles:true}))}if(e){e.value=d.enemies[i]||'';e.dispatchEvent(new Event('change',{bubbles:true}))}});activateView('drafts')}
function encodeDraft(d){return btoa(unescape(encodeURIComponent(JSON.stringify({a:d.allies,e:d.enemies})))).replace(/=+$/,'').replace(/\+/g,'-').replace(/\//g,'_')}
function decodeDraft(s){try{const raw=s.replace(/-/g,'+').replace(/_/g,'/');const pad=raw+'==='.slice((raw.length+3)%4);return JSON.parse(decodeURIComponent(escape(atob(pad))))}catch{return null}}
document.getElementById('saveFreeDraft')?.addEventListener('click',()=>{const d=freeDraft();const items=loadHistory();items.unshift(d);writeHistory(items);renderHistory()});
document.getElementById('shareFreeDraft')?.addEventListener('click',async()=>{const d=freeDraft(),url=new URL(location.href);url.searchParams.set('draft',encodeDraft(d));try{await navigator.clipboard.writeText(url.toString());alert('Enlace del draft copiado.')}catch{prompt('Copia este enlace:',url.toString())}});
const param=new URL(location.href).searchParams.get('draft');if(param){const d=decodeDraft(param);if(d&&Array.isArray(d.a)&&Array.isArray(d.e)){setTimeout(()=>restore({allies:d.a,enemies:d.e}),400)}}
renderHistory();
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Enhanced homepage UX, mobile navigation, local draft history and shareable links')
