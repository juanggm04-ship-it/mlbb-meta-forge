from pathlib import Path

PAGE=Path('index.html')
if not PAGE.exists():
    raise RuntimeError('index.html is required for mobile Draft Coach tabs')

html=PAGE.read_text(encoding='utf-8')
if 'id="coachMobileTabs"' in html:
    print('Mobile Draft Coach tabs already injected')
    raise SystemExit(0)
if 'id="draftCoach"' not in html or 'id="allyPicks"' not in html or 'id="enemyPicks"' not in html:
    raise RuntimeError('Draft Coach must exist before mobile tabs are injected')

CSS='''<style id="coach-mobile-tabs-style">
.coach-mobile-tabs{display:none}
@media(max-width:760px){
  .coach-mobile-tabs{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:16px 0 4px;padding:5px;border:1px solid #2b3d59;border-radius:14px;background:#08111e}
  .coach-mobile-tab{min-height:46px;border:0;border-radius:10px;background:transparent;color:#8fa1bc;padding:9px 10px;font:850 12px/1.2 system-ui;cursor:pointer}
  .coach-mobile-tab span{display:block;margin-top:4px;font-size:9px;color:#71839f;font-weight:800}
  .coach-mobile-tab[aria-selected="true"]{background:#14243a;color:#edf7ff;box-shadow:inset 0 0 0 1px #3e5b7d}
  .coach-mobile-tab[aria-selected="true"] span{color:#72e7ef}
  .coach-panel.coach-mobile-hidden{display:none}
  .coach-grid{grid-template-columns:1fr!important}
}
</style>'''

TABS='''<div id="coachMobileTabs" class="coach-mobile-tabs" role="tablist" aria-label="Lado del Draft Coach"><button id="coachTabAllies" class="coach-mobile-tab" type="button" role="tab" aria-selected="true" aria-controls="coachAlliesPanel" data-coach-side="allies">Tu equipo<span id="coachAlliesCount">0/5 picks</span></button><button id="coachTabEnemies" class="coach-mobile-tab" type="button" role="tab" aria-selected="false" aria-controls="coachEnemiesPanel" data-coach-side="enemies">Rivales<span id="coachEnemiesCount">0/5 picks</span></button></div>'''

marker='<div class="coach-grid">'
if marker not in html:
    raise RuntimeError('Draft Coach grid marker missing')
html=html.replace(marker,TABS+marker,1)

JS=r'''<script id="coach-mobile-tabs-runtime">
(()=>{
 const root=document.getElementById('draftCoach'),tabs=document.getElementById('coachMobileTabs');
 if(!root||!tabs)return;
 const allyPicks=document.getElementById('allyPicks'),enemyPicks=document.getElementById('enemyPicks');
 const allyPanel=allyPicks?.closest('.coach-panel'),enemyPanel=enemyPicks?.closest('.coach-panel');
 const allyTab=document.getElementById('coachTabAllies'),enemyTab=document.getElementById('coachTabEnemies');
 const allyCount=document.getElementById('coachAlliesCount'),enemyCount=document.getElementById('coachEnemiesCount');
 if(!allyPanel||!enemyPanel||!allyTab||!enemyTab||!allyCount||!enemyCount)return;
 allyPanel.id='coachAlliesPanel';enemyPanel.id='coachEnemiesPanel';
 allyPanel.setAttribute('role','tabpanel');enemyPanel.setAttribute('role','tabpanel');
 allyPanel.setAttribute('aria-labelledby','coachTabAllies');enemyPanel.setAttribute('aria-labelledby','coachTabEnemies');
 const media=window.matchMedia('(max-width:760px)');let active='allies';
 function filled(prefix){return [0,1,2,3,4].filter(i=>document.getElementById(prefix+i)?.value).length}
 function syncCounts(){allyCount.textContent=filled('a')+'/5 picks';enemyCount.textContent=filled('e')+'/5 picks'}
 function sync(){
   const mobile=media.matches;
   const alliesOn=active==='allies';
   allyTab.setAttribute('aria-selected',alliesOn?'true':'false');enemyTab.setAttribute('aria-selected',alliesOn?'false':'true');
   allyTab.tabIndex=alliesOn?0:-1;enemyTab.tabIndex=alliesOn?-1:0;
   allyPanel.classList.toggle('coach-mobile-hidden',mobile&&!alliesOn);enemyPanel.classList.toggle('coach-mobile-hidden',mobile&&alliesOn);
   allyPanel.setAttribute('aria-hidden',mobile&&!alliesOn?'true':'false');enemyPanel.setAttribute('aria-hidden',mobile&&alliesOn?'true':'false');
   syncCounts();
 }
 function select(side,focusPanel=false){active=side;sync();if(focusPanel&&media.matches){const panel=side==='allies'?allyPanel:enemyPanel;panel.querySelector('select')?.focus({preventScroll:true});panel.scrollIntoView({behavior:'smooth',block:'nearest'})}}
 allyTab.addEventListener('click',()=>select('allies',true));enemyTab.addEventListener('click',()=>select('enemies',true));
 tabs.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight'].includes(e.key))return;e.preventDefault();select(active==='allies'?'enemies':'allies',false);(active==='allies'?allyTab:enemyTab).focus()});
 root.addEventListener('change',e=>{if(e.target.matches('#allyPicks select,#enemyPicks select'))syncCounts()});
 if(media.addEventListener)media.addEventListener('change',sync);else media.addListener(sync);
 sync();
})();
</script>'''

html=html.replace('</head>',CSS+'</head>',1)
html=html.replace('</body>',JS+'</body>',1)
PAGE.write_text(html,encoding='utf-8')
print('Enhanced Draft Coach mobile UX: segmented allies/enemies tabs with live 0-5 pick counts; desktop keeps both panels visible')
