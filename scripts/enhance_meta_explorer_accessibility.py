from pathlib import Path

PAGE=Path('explore/index.html')
if not PAGE.exists(): raise RuntimeError('Meta Explorer page missing')
page=PAGE.read_text(encoding='utf-8')
if 'id="explorerKeyboardRuntime"' in page:
    print('Explorer keyboard controls already present')
    raise SystemExit

anchor='<button id="copyExplorer" type="button">Copiar vista</button>'
if anchor not in page: raise RuntimeError('Explorer toolbar anchor missing')
controls=anchor+'<button id="swapExplorerAxes" type="button" title="Intercambiar las métricas X/Y">⇄ Ejes</button><button id="resetExplorerView" type="button" title="Volver a Pick vs WR y limpiar la selección">↺ Reset</button>'
page=page.replace(anchor,controls,1)
css='''<style id="explorer-keyboard-style">.dot[tabindex="0"]:focus{outline:none;stroke:#ffffff;stroke-width:4;filter:drop-shadow(0 0 5px #55e7ff)}#swapExplorerAxes,#resetExplorerView{white-space:nowrap}</style>'''
js='''<script id="explorerKeyboardRuntime">(()=>{const svg=document.getElementById('metaPlot'),xs=document.getElementById('xMetric'),ys=document.getElementById('yMetric'),search=document.getElementById('exploreSearch'),swap=document.getElementById('swapExplorerAxes'),reset=document.getElementById('resetExplorerView');if(!svg||!xs||!ys)return;function upgrade(){for(const c of svg.querySelectorAll('.dot')){c.setAttribute('tabindex','0');c.setAttribute('role','button');const t=c.querySelector('title')?.textContent||'Héroe del mapa';c.setAttribute('aria-label','Seleccionar '+t)}}upgrade();new MutationObserver(upgrade).observe(svg,{childList:true});svg.addEventListener('keydown',e=>{const c=e.target.closest?.('.dot');if(!c)return;if(e.key==='Enter'||e.key===' '){e.preventDefault();c.dispatchEvent(new MouseEvent('click',{bubbles:true}))}});swap?.addEventListener('click',()=>{const x=xs.value;xs.value=ys.value;ys.value=x;xs.dispatchEvent(new Event('change',{bubbles:true}))});reset?.addEventListener('click',()=>{const clean=location.pathname;location.assign(clean)});})();</script>'''
page=page.replace('</head>',css+'</head>',1)
page=page.replace('</body>',js+'</body>',1)
PAGE.write_text(page,encoding='utf-8')
print('Meta Explorer accessibility controls injected: keyboard_points=true; swap_axes=true; reset_view=true')
