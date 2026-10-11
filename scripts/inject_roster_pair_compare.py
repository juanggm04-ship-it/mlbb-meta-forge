from pathlib import Path

ROSTER=Path('roster/index.html')
if not ROSTER.exists():
    raise RuntimeError('roster/index.html is required for pair comparison')

page=ROSTER.read_text(encoding='utf-8')
if 'id="roster-pair-compare-script"' in page:
    print('Roster pair comparison already injected')
    raise SystemExit(0)
if 'id="roster-product-cards-script"' not in page or 'id="rosterFilters"' not in page:
    raise RuntimeError('Roster product cards must be enhanced before pair comparison')

CSS='''<style id="roster-pair-compare-style">
.roster-card-actions .select{color:#92a7c7}.roster-card-actions .select.active,.roster-card-actions .select[aria-pressed="true"]{background:#8b70ff;color:#07101b;border-color:#8b70ff}.roster-compare-tray{display:none;align-items:center;gap:10px;flex-wrap:wrap;margin:-3px 0 16px;padding:12px;border:1px solid #344968;border-radius:16px;background:linear-gradient(135deg,#0a1423,#151329);box-shadow:0 12px 28px #0003}.roster-compare-tray.visible{display:flex}.roster-compare-slots{display:flex;align-items:center;gap:7px;flex:1;min-width:260px}.roster-compare-slot{display:flex;align-items:center;justify-content:center;min-width:120px;min-height:38px;padding:9px 11px;border:1px dashed #3a4d69;border-radius:11px;color:#7587a3;font-size:10px;font-weight:850;background:#09111d}.roster-compare-slot.filled{border-style:solid;border-color:#6e5b9d;color:#d8cdfd;background:#111329}.roster-compare-vs{font-size:9px;font-weight:950;color:#6f819d}.roster-compare-actions{display:flex;gap:7px;align-items:center}.roster-compare-actions a,.roster-compare-actions button{display:inline-flex;align-items:center;justify-content:center;min-height:38px;padding:9px 12px;border:1px solid #30445f;border-radius:11px;background:#0b1524;color:#d8e5f7;text-decoration:none;font:850 10px/1 system-ui;cursor:pointer}.roster-compare-actions a.ready{background:linear-gradient(135deg,#4de5ff,#8b70ff);color:#07101b;border:0}.roster-compare-actions a[aria-disabled="true"]{opacity:.45;pointer-events:none}.roster-compare-status{width:100%;margin:0;color:#8192ad;font-size:9px;line-height:1.45}.roster-compare-status.warn{color:#ffd27c}@media(max-width:620px){.roster-compare-tray{align-items:stretch}.roster-compare-slots{width:100%;min-width:0}.roster-compare-slot{min-width:0;flex:1}.roster-compare-actions{width:100%}.roster-compare-actions a,.roster-compare-actions button{flex:1}}
</style>'''

TRAY='''<section id="rosterCompareTray" class="roster-compare-tray" aria-label="Comparar dos héroes seleccionados"><div class="roster-compare-slots"><span id="rosterCompareSlotA" class="roster-compare-slot">Elige héroe A</span><span class="roster-compare-vs">VS</span><span id="rosterCompareSlotB" class="roster-compare-slot">Elige héroe B</span></div><div class="roster-compare-actions"><a id="rosterCompareSelected" href="../compare/" aria-disabled="true">⚔ Comparar seleccionados</a><button id="rosterCompareClear" type="button">Limpiar</button></div><p id="rosterCompareStatus" class="roster-compare-status" aria-live="polite">Selecciona hasta 2 héroes. Esta selección es temporal y no modifica tu Watchlist.</p></section>'''

marker='<div id="rosterSortNote"'
idx=page.find(marker)
if idx==-1:
    raise RuntimeError('Roster sort note marker missing for comparison tray')
page=page[:idx]+TRAY+page[idx:]

JS='''<script id="roster-pair-compare-script">(()=>{const grid=document.getElementById('grid'),tray=document.getElementById('rosterCompareTray'),slotA=document.getElementById('rosterCompareSlotA'),slotB=document.getElementById('rosterCompareSlotB'),go=document.getElementById('rosterCompareSelected'),clear=document.getElementById('rosterCompareClear'),status=document.getElementById('rosterCompareStatus');if(!grid||!tray||!slotA||!slotB||!go||!clear||!status)return;const selected=[];function sync(){slotA.textContent=selected[0]||'Elige héroe A';slotB.textContent=selected[1]||'Elige héroe B';slotA.classList.toggle('filled',!!selected[0]);slotB.classList.toggle('filled',!!selected[1]);tray.classList.toggle('visible',selected.length>0);document.querySelectorAll('[data-compare-select]').forEach(b=>{const on=selected.includes(b.dataset.compareSelect);b.classList.toggle('active',on);b.setAttribute('aria-pressed',on?'true':'false');b.textContent=on?'✓ Seleccionado':'＋ Seleccionar'});if(selected.length===2){go.href='../compare/?a='+encodeURIComponent(selected[0])+'&b='+encodeURIComponent(selected[1]);go.classList.add('ready');go.setAttribute('aria-disabled','false');status.classList.remove('warn');status.textContent='Pareja lista. Hero Compare abrirá ambos héroes ya cargados.'}else{go.href='../compare/';go.classList.remove('ready');go.setAttribute('aria-disabled','true');if(!status.classList.contains('warn'))status.textContent='Selecciona hasta 2 héroes. Esta selección es temporal y no modifica tu Watchlist.'}}function enhanceCards(){grid.querySelectorAll('.roster-card').forEach(card=>{if(card.querySelector('[data-compare-select]'))return;const actions=card.querySelector('.roster-card-actions'),name=card.dataset.hero;if(!actions||!name)return;const b=document.createElement('button');b.type='button';b.className='select';b.dataset.compareSelect=name;b.setAttribute('aria-pressed','false');b.textContent='＋ Seleccionar';actions.insertBefore(b,actions.querySelector('.open'));});sync()}grid.addEventListener('click',e=>{const b=e.target.closest('[data-compare-select]');if(!b)return;const name=b.dataset.compareSelect,i=selected.indexOf(name);if(i>=0){selected.splice(i,1);status.classList.remove('warn')}else if(selected.length<2){selected.push(name);status.classList.remove('warn')}else{status.classList.add('warn');status.textContent='Ya hay 2 héroes seleccionados. Quita uno antes de elegir otro.'}sync()});clear.addEventListener('click',()=>{selected.length=0;status.classList.remove('warn');sync()});new MutationObserver(enhanceCards).observe(grid,{childList:true});enhanceCards()})();</script>'''

page=page.replace('</head>',CSS+'</head>',1)
page=page.replace('</body>',JS+'</body>',1)
ROSTER.write_text(page,encoding='utf-8')
print('Roster pair comparison injected: temporary selection, max=2, direct Hero Compare route')
