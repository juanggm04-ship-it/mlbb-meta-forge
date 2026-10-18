from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="homeQuickActions"' in html:
    print('Home UX already enhanced')
    raise SystemExit

css='''<style>
.quick-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:18px 0 0}.quick-action{border:1px solid #2a3a59;background:linear-gradient(145deg,#0d1626,#111a2c);border-radius:16px;padding:15px;text-align:left;color:#eaf2ff;cursor:pointer}.quick-action b{display:block;font-size:14px}.quick-action span{display:block;margin-top:4px;color:#7f90ad;font-size:11px;line-height:1.4}.draft-library{margin-top:18px;padding:18px;border:1px solid #263652;border-radius:18px;background:#0a111f}.draft-library-head{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}.draft-library h4{margin:0}.draft-library-actions{display:flex;gap:8px;flex-wrap:wrap}.draft-library-actions button{border:1px solid #33435f;background:#111a2c;color:#dbe6f7;border-radius:10px;padding:9px 11px;cursor:pointer}.draft-history{display:grid;gap:8px;margin-top:12px}.draft-history-item{display:flex;justify-content:space-between;gap:10px;align-items:center;padding:10px 12px;border:1px solid #263650;border-radius:12px;background:#0c1423}.draft-history-item span{color:#8796b1;font-size:11px}.draft-history-item button{border:1px solid #30425f;background:#121d31;color:#dbe7f8;border-radius:9px;padding:7px 9px;cursor:pointer}.mobile-dock{display:none}.home-reset-filter{border:1px solid #334461;background:#0b1322;color:#b9c5da;border-radius:12px;padding:11px 13px;cursor:pointer;font-weight:800}.home-reset-filter:hover,.home-reset-filter:focus-visible{border-color:#5bdce9;color:#eafcff}.home-grid-tools{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin:14px 0 2px}.home-result-status{color:#98aac5;font-size:12px;line-height:1.5}.home-show-more{min-height:44px;border:1px solid #35506d;background:#102137;color:#dcecff;border-radius:12px;padding:10px 14px;cursor:pointer;font-weight:800}.home-show-more:hover,.home-show-more:focus-visible{border-color:#6be6ee;background:#16304a}.favorite-btn{min-width:44px!important;min-height:44px!important;width:44px!important;height:44px!important}.card.home-card-hidden{display:none!important}.card[role="button"]:focus-visible{outline:3px solid #46e6ff;outline-offset:3px}.filters button .home-filter-count{opacity:.72;font-size:.82em;margin-left:3px}@media(max-width:760px){.quick-actions{grid-template-columns:1fr}.mobile-dock{position:fixed;left:12px;right:12px;bottom:12px;z-index:45;display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:6px;background:#0a101ddd;border:1px solid #2b3956;border-radius:16px;backdrop-filter:blur(14px);box-shadow:0 18px 50px #0009}.mobile-dock button{border:0;background:#111a2c;color:#dbe7f8;border-radius:11px;padding:10px 6px;font-size:11px;font-weight:800}.mobile-dock button.active{background:#46e6ff;color:#061019}body{padding-bottom:78px}.home-grid-tools{align-items:stretch}.home-show-more{width:100%}}
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
function decodeDraft(s){try{const raw=s.replace(/-/g,'+').replace(/_/g,'/');const pad=raw+'='.repeat((4-raw.length%4)%4);return JSON.parse(decodeURIComponent(escape(atob(pad))))}catch{return null}}
document.getElementById('saveFreeDraft')?.addEventListener('click',()=>{const d=freeDraft();const items=loadHistory();items.unshift(d);writeHistory(items);renderHistory()});
document.getElementById('shareFreeDraft')?.addEventListener('click',async()=>{const d=freeDraft(),url=new URL(location.href);url.searchParams.set('draft',encodeDraft(d));try{await navigator.clipboard.writeText(url.toString());alert('Enlace del draft copiado.')}catch{prompt('Copia este enlace:',url.toString())}});
const param=new URL(location.href).searchParams.get('draft');if(param){const d=decodeDraft(param);if(d&&Array.isArray(d.a)&&Array.isArray(d.e)){setTimeout(()=>restore({allies:d.a,enemies:d.e}),400)}}
renderHistory();

// Keep the homepage roster fast to scan without hiding access to the full result set.
const grid=document.getElementById('heroGrid'),search=document.getElementById('heroSearch'),sort=document.getElementById('sortHeroes'),favFilter=document.getElementById('favoriteFilter'),filterBox=document.getElementById('filters');
if(grid){
  const BATCH=24;
  let visible=BATCH,scheduled=false;
  const toolbar=document.createElement('div');toolbar.className='home-grid-tools';toolbar.innerHTML='<span id="homeResultStatus" class="home-result-status" role="status" aria-live="polite"></span><button id="homeShowMore" class="home-show-more" type="button">Mostrar más héroes</button>';grid.insertAdjacentElement('afterend',toolbar);
  const reset=document.createElement('button');reset.id='homeResetFilters';reset.className='home-reset-filter';reset.type='button';reset.textContent='Restablecer filtros';document.querySelector('.searchbar')?.appendChild(reset);
  const status=document.getElementById('homeResultStatus'),more=document.getElementById('homeShowMore');
  function heroName(card){return card.querySelector('.hero')?.textContent?.trim()||'héroe'}
  function enhanceCard(card){
    const name=heroName(card);card.setAttribute('role','button');card.tabIndex=0;card.setAttribute('aria-label',`Abrir ficha de ${name}`);
    if(!card.dataset.keyboardReady){card.dataset.keyboardReady='1';card.addEventListener('keydown',e=>{if(e.target!==card)return;if(e.key==='Enter'||e.key===' '){e.preventDefault();card.click()}})}
    card.querySelectorAll('img').forEach(img=>{img.loading='lazy';img.decoding='async'});
    const fav=card.querySelector('.favorite-btn');if(fav){const active=fav.classList.contains('active');fav.setAttribute('aria-label',`${active?'Quitar':'Añadir'} ${name} ${active?'de':'a'} favoritos`);fav.setAttribute('aria-pressed',String(active));fav.title=active?'Quitar de favoritos':'Añadir a favoritos'}
  }
  function decorateFilterCounts(){
    [...filterBox?.querySelectorAll('button')||[]].forEach(btn=>{if(btn.querySelector('.home-filter-count'))return;const label=btn.textContent.trim();const count=label==='Todos'?DATA.heroes.length:DATA.heroes.filter(h=>h.lane===label).length;btn.insertAdjacentHTML('beforeend',`<span class="home-filter-count" aria-hidden="true">· ${count}</span>`);btn.setAttribute('aria-label',`${label}: ${count} héroes`)})
  }
  function applyBrowseState(){
    scheduled=false;const cards=[...grid.querySelectorAll('.card')];cards.forEach(enhanceCard);cards.forEach((card,i)=>card.classList.toggle('home-card-hidden',i>=visible));decorateFilterCounts();
    const shown=Math.min(cards.length,visible);more.hidden=cards.length<=visible;
    if(showFav&&cards.length===0)status.textContent='No tienes favoritos en esta vista. Marca una estrella para crear tu lista.';
    else if(cards.length===0)status.textContent='No hay héroes que coincidan con estos filtros.';
    else status.textContent=`Mostrando ${shown} de ${cards.length} héroes en esta vista.`;
  }
  function schedule(){if(scheduled)return;scheduled=true;requestAnimationFrame(applyBrowseState)}
  new MutationObserver(schedule).observe(grid,{childList:true});
  more.addEventListener('click',()=>{visible+=BATCH;applyBrowseState();if(more.hidden)status.focus?.()});
  function resetBatch(){visible=BATCH;setTimeout(schedule,0)}
  search?.addEventListener('input',resetBatch);sort?.addEventListener('change',resetBatch);favFilter?.addEventListener('click',resetBatch);filterBox?.addEventListener('click',resetBatch);
  reset.addEventListener('click',()=>{search.value='';sort.value='tier';showFav=false;lane='Todos';favFilter?.classList.remove('active');visible=BATCH;render();search.focus()});
  schedule();
}
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Enhanced homepage UX, mobile navigation, accessible hero browsing, local draft history and shareable links')
