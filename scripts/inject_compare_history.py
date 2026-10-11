from pathlib import Path

PAGE=Path('compare/index.html')
if not PAGE.exists():
    raise RuntimeError('compare/index.html is required for recent compare history')
page=PAGE.read_text(encoding='utf-8')
if 'id="compare-recent-script"' in page:
    print('Recent Hero Compare history already injected')
    raise SystemExit(0)
if 'id="a"' not in page or 'id="b"' not in page:
    raise RuntimeError('Hero Compare selectors missing')

CSS='''<style id="compare-recent-style">.compare-recent{margin-top:16px;padding:16px;border:1px solid #293c58;border-radius:18px;background:#09121f}.compare-recent-head{display:flex;justify-content:space-between;align-items:center;gap:10px}.compare-recent-head h2{font-size:16px;margin:0}.compare-recent-head button{border:1px solid #30445f;border-radius:10px;background:#0d1725;color:#93a5bf;padding:8px 10px;font:800 9px/1 system-ui;cursor:pointer}.compare-recent-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:11px}.compare-recent-item{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 11px;border:1px solid #263953;border-radius:12px;background:#0b1523;color:#dce8f8;text-decoration:none}.compare-recent-item b{font-size:11px}.compare-recent-item span{font-size:9px;color:#8294af}.compare-recent-empty,.compare-recent-note{color:#8294af;font-size:10px;line-height:1.5}.compare-recent-note{margin:9px 0 0}@media(max-width:620px){.compare-recent-list{grid-template-columns:1fr}}</style>'''
PANEL='''<section id="compareRecent" class="compare-recent"><div class="compare-recent-head"><h2>Comparaciones recientes</h2><button id="compareRecentClear" type="button">Limpiar historial</button></div><div id="compareRecentList" class="compare-recent-list"></div><p class="compare-recent-note">Se guarda solo en este navegador. Máximo 6 parejas; A vs B y B vs A cuentan como la misma pareja.</p></section>'''
marker='</main>'
if marker not in page: raise RuntimeError('Hero Compare main closing marker missing')
page=page.replace(marker,PANEL+marker,1)
JS='''<script id="compare-recent-script">(()=>{const KEY='mf_compare_recent_v1',MAX=6,a=document.getElementById('a'),b=document.getElementById('b'),list=document.getElementById('compareRecentList'),clear=document.getElementById('compareRecentClear');if(!a||!b||!list||!clear)return;const pairKey=(x,y)=>[x,y].sort((m,n)=>m.localeCompare(n)).join(':::');function read(){try{const v=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(v)?v:[]}catch{return []}}function write(v){try{localStorage.setItem(KEY,JSON.stringify(v.slice(0,MAX)))}catch{}}function render(){const rows=read();list.replaceChildren();if(!rows.length){const e=document.createElement('div');e.className='compare-recent-empty';e.textContent='Todavía no hay comparaciones guardadas en este navegador.';list.appendChild(e);return}rows.forEach(r=>{const link=document.createElement('a'),label=document.createElement('b'),meta=document.createElement('span'),u=new URL('../compare/',location.href);u.searchParams.set('a',r.a);u.searchParams.set('b',r.b);link.className='compare-recent-item';link.href=u.href;label.textContent=r.a+'  VS  '+r.b;meta.textContent='Abrir →';link.append(label,meta);list.appendChild(link)})}function remember(){const x=a.value,y=b.value;if(!x||!y||x===y)return;const key=pairKey(x,y),rows=read().filter(r=>r&&r.key!==key);rows.unshift({a:x,b:y,key,ts:Date.now()});write(rows);render()}a.addEventListener('change',()=>queueMicrotask(remember));b.addEventListener('change',()=>queueMicrotask(remember));clear.addEventListener('click',()=>{try{localStorage.removeItem(KEY)}catch{}render()});render();queueMicrotask(remember)})();</script>'''
page=page.replace('</head>',CSS+'</head>',1)
page=page.replace('</body>',JS+'</body>',1)
PAGE.write_text(page,encoding='utf-8')
print('Injected local recent Hero Compare history: max=6; unordered-pair dedupe; localStorage only')
