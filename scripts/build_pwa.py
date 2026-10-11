from pathlib import Path
import os

ROOT=Path('.')
version=(os.getenv('GITHUB_SHA') or 'dev')[:12]
cache_name=f'mf-shell-{version}'

OFFLINE='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#070a12"><link rel="manifest" href="manifest.webmanifest"><title>Sin conexión · Meta Forge</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;padding:22px;background:#070a12;color:#eef5ff;font-family:system-ui}.box{max-width:620px;padding:28px;border:1px solid #2a3b58;border-radius:24px;background:#0c1422}h1{margin:0 0 10px;font-size:clamp(34px,8vw,62px);letter-spacing:-.05em}p{color:#9bacbf;line-height:1.65}a{display:inline-flex;margin-top:10px;padding:11px 14px;border-radius:12px;background:#51e4ff;color:#07101b;text-decoration:none;font-weight:900}</style></head><body><main class="box"><small>MLBB META FORGE</small><h1>Sin conexión</h1><p>No pudimos llegar a la red. Si ya visitaste una sección, Meta Forge intentará mostrar la copia guardada en este dispositivo.</p><a href="./">Volver al inicio</a></main></body></html>'''
Path('offline.html').write_text(OFFLINE,encoding='utf-8')

core=['./','./roster/','./trends/','./compare/','./my-meta/','./methodology.html','./privacy.html','./terms.html','./manifest.webmanifest','./assets/icon.svg','./data/live-meta.json','./data/meta-score.json','./data/meta-score-history.json','./offline.html']
required=['index.html','roster/index.html','trends/index.html','compare/index.html','my-meta/index.html','methodology.html','privacy.html','terms.html','manifest.webmanifest','assets/icon.svg','data/live-meta.json','data/meta-score.json','data/meta-score-history.json','offline.html']
missing=[p for p in required if not Path(p).exists()]
if missing:
    raise RuntimeError('PWA core dependencies missing: '+', '.join(missing))
core_js=','.join(repr(x) for x in core)
SW=f'''const CACHE={cache_name!r};\nconst CORE=[{core_js}];\nself.addEventListener('install',event=>{{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE)).then(()=>self.skipWaiting()))}});\nself.addEventListener('activate',event=>{{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('mf-shell-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});\nasync function networkFirst(request,offline=false){{const cache=await caches.open(CACHE);try{{const response=await fetch(request);if(response&&response.ok)cache.put(request,response.clone());return response}}catch{{return (await cache.match(request))||(offline?await cache.match('./offline.html'):Response.error())}}}}\nself.addEventListener('fetch',event=>{{const request=event.request;if(request.method!=='GET')return;const url=new URL(request.url);if(url.origin!==self.location.origin)return;if(request.mode==='navigate'){{event.respondWith(networkFirst(request,true));return}}if(url.pathname.includes('/data/')&&url.pathname.endsWith('.json')){{event.respondWith(networkFirst(request,false));return}}event.respondWith((async()=>{{const cache=await caches.open(CACHE),cached=await cache.match(request);const network=fetch(request).then(response=>{{if(response&&response.ok)cache.put(request,response.clone());return response}}).catch(()=>null);return cached||(await network)||Response.error()}})())}});\n'''
Path('sw.js').write_text(SW,encoding='utf-8')

reduced='''<style id="mf-reduced-motion">@media (prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}</style>'''
pwa_css='''<style id="mf-pwa-style">#mfOfflineStatus{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:99999;padding:9px 12px;border:1px solid #6d5a36;border-radius:999px;background:#1a150d;color:#ffd27c;font:850 10px/1.2 system-ui;box-shadow:0 10px 30px #0007}#installMetaForge{position:fixed;right:18px;bottom:18px;z-index:99998;border:1px solid #4ddff3;border-radius:999px;background:#0c1a28;color:#5de9ff;padding:10px 13px;font:900 10px/1 system-ui;cursor:pointer;box-shadow:0 10px 30px #0007}</style>'''

def prefix_for(path):
    depth=len(path.parent.parts)
    return '../'*depth

count=0
for path in ROOT.rglob('*.html'):
    if path.name=='offline.html' or '.git' in path.parts:
        continue
    text=path.read_text(encoding='utf-8')
    prefix=prefix_for(path)
    if 'rel="manifest"' not in text:
        text=text.replace('</head>',f'<link rel="manifest" href="{prefix}manifest.webmanifest">'+reduced+pwa_css+'</head>',1)
    else:
        if 'id="mf-reduced-motion"' not in text: text=text.replace('</head>',reduced+pwa_css+'</head>',1)
    if 'id="mf-pwa-runtime"' not in text:
        banner='<div id="mfOfflineStatus" role="status" hidden>Sin conexión · mostrando contenido guardado cuando esté disponible</div>'
        install=''
        if path==Path('index.html'):
            install='<button id="installMetaForge" type="button" hidden>Instalar Meta Forge</button>'
        runtime=f'''<script id="mf-pwa-runtime">(()=>{{const banner=document.getElementById('mfOfflineStatus');function syncOnline(){{if(banner)banner.hidden=navigator.onLine}}window.addEventListener('online',syncOnline);window.addEventListener('offline',syncOnline);syncOnline();if('serviceWorker' in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('{prefix}sw.js').catch(()=>{{}}));const install=document.getElementById('installMetaForge');let promptEvent=null;window.addEventListener('beforeinstallprompt',e=>{{e.preventDefault();promptEvent=e;if(install)install.hidden=false}});if(install)install.addEventListener('click',async()=>{{if(!promptEvent)return;promptEvent.prompt();await promptEvent.userChoice;promptEvent=null;install.hidden=true}});window.addEventListener('appinstalled',()=>{{promptEvent=null;if(install)install.hidden=true}})}})();</script>'''
        text=text.replace('</body>',banner+install+runtime+'</body>',1)
    path.write_text(text,encoding='utf-8')
    count+=1
print(f'PWA shell built: version={version}; cache={cache_name}; html_pages={count}; core={len(core)}')
