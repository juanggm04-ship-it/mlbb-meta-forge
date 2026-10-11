from pathlib import Path
import json,re,unicodedata

PAGE=Path('my-meta/index.html')
LIVE=Path('data/live-meta.json')
if not PAGE.exists() or not LIVE.exists():
    raise RuntimeError('My Meta and live roster are required for Watchlist sharing')
page=PAGE.read_text(encoding='utf-8')
if 'id="watchlistShare"' in page:
    print('Watchlist sharing already injected')
    raise SystemExit(0)
heroes=[h.get('name') for h in json.loads(LIVE.read_text(encoding='utf-8')).get('heroes',[]) if h.get('name')]
if len(heroes)!=133:
    raise RuntimeError(f'Expected 133 live heroes, got {len(heroes)}')

def slug(name):
    s=''.join(c for c in unicodedata.normalize('NFD',name.lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')
slug_map={slug(n):n for n in heroes}
if len(slug_map)!=len(heroes):
    raise RuntimeError('Hero slug collision blocks shareable Watchlist')
MAP=json.dumps(slug_map,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
CSS='''<style id="watchlist-share-style">.watch-share{margin-top:14px;padding:15px;border:1px solid #2a3d58;border-radius:17px;background:#0a1321}.watch-share-head{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}.watch-share-head h2{margin:2px 0;font-size:17px}.watch-share p{margin:7px 0 0;color:#8294ad;font-size:10px;line-height:1.55}.watch-share-actions{display:flex;gap:8px;flex-wrap:wrap}.watch-share button{display:inline-flex;align-items:center;min-height:36px;padding:9px 11px;border:1px solid #30445f;border-radius:10px;background:#0e1929;color:#d8e5f6;font:850 10px/1 system-ui;cursor:pointer}.watch-share button:hover,.watch-share button:focus-visible{outline:none;border-color:#54e5ff}.watch-share button.primary{border-color:#2f6a75;color:#6deaff}.watch-share button.warn{border-color:#6a5037;color:#ffd18b}.watch-share-list{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}.watch-share-chip{padding:5px 7px;border:1px solid #2d405b;border-radius:999px;color:#b9c7da;font-size:9px}.watch-share-status{margin-top:8px;color:#8496b0;font-size:10px}.watch-share-status.ok{color:#7ce9bf}.watch-share-status.warn{color:#ffd27c}</style>'''
PANEL='''<section id="watchlistShare" class="watch-share"><div class="watch-share-head"><div><small>WATCHLIST · SHARE</small><h2>Comparte tu pool</h2></div><div class="watch-share-actions"><button id="shareWatchlist" class="primary" type="button">Compartir Watchlist</button></div></div><p>El enlace contiene solo los nombres de los héroes seguidos. Quien lo abra verá una vista previa y decidirá si quiere añadirlos o reemplazar su propia Watchlist.</p><div id="sharedWatchlistPreview" hidden></div><p id="watchlistShareStatus" class="watch-share-status" aria-live="polite"></p></section>'''
marker='</main>'
if marker not in page:
    raise RuntimeError('My Meta closing main marker missing')
page=page.replace(marker,PANEL+marker,1)
JS=f'''<script id="watchlist-share-script">(()=>{{const WATCH='mf_watchlist_v1',SLUG_TO_NAME={MAP},NAME_TO_SLUG=new Map(Object.entries(SLUG_TO_NAME).map(([s,n])=>[n,s])),share=document.getElementById('shareWatchlist'),preview=document.getElementById('sharedWatchlistPreview'),status=document.getElementById('watchlistShareStatus');if(!share||!preview||!status)return;function read(){{try{{const v=JSON.parse(localStorage.getItem(WATCH)||'[]');return Array.isArray(v)?v.filter(n=>NAME_TO_SLUG.has(n)):[]}}catch{{return []}}}}function uniq(v){{return [...new Set(v)]}}function say(t,k=''){{status.textContent=t;status.className='watch-share-status'+(k?' '+k:'')}}function decode(raw){{if(!raw)return[];return uniq(raw.split(',').map(s=>SLUG_TO_NAME[s]).filter(Boolean)).slice(0,133)}}function clearParam(){{const u=new URL(location.href);u.searchParams.delete('shared');history.replaceState(null,'',u.pathname+(u.searchParams.toString()?'?'+u.searchParams.toString():'')+u.hash)}}async function copyOrShare(url){{if(navigator.share){{try{{await navigator.share({{title:'Mi Watchlist · MLBB Meta Forge',text:'Mi pool seguido en Meta Forge',url}});say('Enlace compartido.','ok');return}}catch(e){{if(e?.name==='AbortError')return}}}}try{{await navigator.clipboard.writeText(url);say('Enlace de Watchlist copiado.','ok')}}catch{{prompt('Copia este enlace:',url)}}}}share.addEventListener('click',()=>{{const names=uniq(read());if(!names.length){{say('Sigue al menos un héroe antes de compartir tu Watchlist.','warn');return}}const u=new URL(location.href);u.searchParams.set('shared',names.map(n=>NAME_TO_SLUG.get(n)).filter(Boolean).join(','));copyOrShare(u.toString())}});const incoming=decode(new URL(location.href).searchParams.get('shared'));if(!incoming.length)return;preview.hidden=false;preview.innerHTML=`<p><b>Watchlist compartida:</b> ${{incoming.length}} héroes. Nada se importará sin tu permiso.</p><div class="watch-share-list">${{incoming.slice(0,30).map(n=>`<span class="watch-share-chip">${{n.replace(/&/g,'&amp;').replace(/</g,'&lt;')}}</span>`).join('')}}${{incoming.length>30?`<span class="watch-share-chip">+${{incoming.length-30}} más</span>`:''}}</div><div class="watch-share-actions" style="margin-top:10px"><button id="sharedMerge" class="primary" type="button">Añadir a mi Watchlist</button><button id="sharedReplace" class="warn" type="button">Reemplazar la mía</button><button id="sharedDismiss" type="button">Cerrar vista previa</button></div>`;document.getElementById('sharedMerge').onclick=()=>{{const merged=uniq([...read(),...incoming]);localStorage.setItem(WATCH,JSON.stringify(merged));say(`Añadidos. Tu Watchlist ahora tiene ${{merged.length}} héroes.`,'ok');clearParam();setTimeout(()=>location.reload(),350)}};document.getElementById('sharedReplace').onclick=()=>{{if(!confirm(`Reemplazar tu Watchlist actual por estos ${{incoming.length}} héroes?`))return;localStorage.setItem(WATCH,JSON.stringify(incoming));say('Watchlist reemplazada.','ok');clearParam();setTimeout(()=>location.reload(),350)}};document.getElementById('sharedDismiss').onclick=()=>{{preview.hidden=true;clearParam();say('Vista previa cerrada. No se modificó tu Watchlist.')}}}})();</script>'''
page=page.replace('</head>',CSS+'</head>',1)
page=page.replace('</body>',JS+'</body>',1)
PAGE.write_text(page,encoding='utf-8')
print(f'Injected shareable Watchlist links: heroes={len(heroes)}; explicit merge/replace consent; no server upload')
