from pathlib import Path
import os, struct, subprocess, zlib, binascii

ROOT=Path('.')
def checked_out_sha():
    try:
        return subprocess.check_output(['git','rev-parse','HEAD'],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:
        return os.getenv('GITHUB_SHA') or 'dev'
build_sha=checked_out_sha()
version=build_sha[:12]
cache_name=f'mf-shell-{version}'

def png_chunk(kind, data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',binascii.crc32(kind+data)&0xffffffff)

def make_icon(size, path):
    raw=bytearray();cx=cy=(size-1)/2
    for y in range(size):
        raw.append(0)
        for x in range(size):
            t=(x+y)/(2*(size-1));r=int(7+(20-7)*t);g=int(10+(18-10)*t);b=int(18+(39-18)*t)
            dx=(x-cx)/size;dy=(y-cy)/size;d2=dx*dx+dy*dy
            if d2<0.16:
                glow=max(0.0,1-(d2/0.16));r=min(255,int(r+20*glow));g=min(255,int(g+28*glow));b=min(255,int(b+45*glow))
            man=abs(dx)+abs(dy)
            if 0.205<man<0.235:
                mix=(x/size);r=int(76+(142-76)*mix);g=int(229+(105-229)*mix);b=255
            if abs(dx)<0.035 and -0.15<dy<0.09:r,g,b=84,232,255
            if -0.035<dx<0.105 and -0.015<dy<0.055 and (dy+0.015)<(0.055-(dx+0.035)*0.5):r,g,b=151,111,255
            if abs(dy-0.13)<0.022 and abs(dx)<0.13:r,g,b=221,230,255
            raw.extend((r,g,b,255))
    ihdr=struct.pack('>IIBBBBB',size,size,8,6,0,0,0)
    png=b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',ihdr)+png_chunk(b'IDAT',zlib.compress(bytes(raw),9))+png_chunk(b'IEND',b'')
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(png)

make_icon(192,Path('assets/icon-192.png'));make_icon(512,Path('assets/icon-512.png'))
OFFLINE='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#070a12"><link rel="manifest" href="manifest.webmanifest"><title>Sin conexión · Meta Forge</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;padding:22px;background:#070a12;color:#eef5ff;font-family:system-ui}.box{max-width:620px;padding:28px;border:1px solid #2a3b58;border-radius:24px;background:#0c1422}h1{margin:0 0 10px;font-size:clamp(34px,8vw,62px);letter-spacing:-.05em}p{color:#9bacbf;line-height:1.65}a{display:inline-flex;margin-top:10px;padding:11px 14px;border-radius:12px;background:#51e4ff;color:#07101b;text-decoration:none;font-weight:900}</style></head><body><main class="box"><small>MLBB META FORGE</small><h1>Sin conexión</h1><p>No pudimos llegar a la red. Si ya visitaste una sección, Meta Forge intentará mostrar la copia guardada en este dispositivo.</p><a href="./">Volver al inicio</a></main></body></html>'''
Path('offline.html').write_text(OFFLINE,encoding='utf-8')
core=['./','./roster/','./explore/','./trends/','./compare/','./my-meta/','./status/','./methodology.html','./privacy.html','./terms.html','./manifest.webmanifest','./assets/icon.svg','./assets/product-design.css','./assets/ux-refinements.css','./assets/icon-192.png','./assets/icon-512.png','./data/live-meta.json','./data/meta-score.json','./data/meta-score-history.json','./data/build-info.json','./data/product-release.json','./offline.html']
required=['index.html','roster/index.html','explore/index.html','trends/index.html','compare/index.html','my-meta/index.html','status/index.html','methodology.html','privacy.html','terms.html','manifest.webmanifest','assets/icon.svg','assets/product-design.css','assets/ux-refinements.css','assets/icon-192.png','assets/icon-512.png','data/live-meta.json','data/meta-score.json','data/meta-score-history.json','data/build-info.json','data/product-release.json','offline.html']
missing=[p for p in required if not Path(p).exists()]
if missing:raise RuntimeError('PWA core dependencies missing: '+', '.join(missing))
core_js=','.join(repr(x) for x in core)
SW=f'''const CACHE={cache_name!r};\nconst CORE=[{core_js}];\nself.addEventListener('install',event=>{{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(CORE)).then(()=>self.skipWaiting()))}});\nself.addEventListener('activate',event=>{{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('mf-shell-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});\nasync function networkFirst(request){{const cache=await caches.open(CACHE);try{{const response=await fetch(request);if(response&&response.ok)cache.put(request,response.clone());return response}}catch{{return (await cache.match(request))||Response.error()}}}}\nfunction navigationKey(request){{const url=new URL(request.url);url.search='';url.hash='';return new Request(url.toString(),{{method:'GET'}})}}\nasync function navigationNetworkFirst(request){{const cache=await caches.open(CACHE),key=navigationKey(request);try{{const response=await fetch(request);if(response&&response.ok)cache.put(key,response.clone());return response}}catch{{return (await cache.match(key))||(await cache.match('./offline.html'))||Response.error()}}}}\nself.addEventListener('fetch',event=>{{const request=event.request;if(request.method!=='GET')return;const url=new URL(request.url);if(url.origin!==self.location.origin)return;if(request.mode==='navigate'){{event.respondWith(navigationNetworkFirst(request));return}}if(url.pathname.includes('/data/')&&url.pathname.endsWith('.json')){{event.respondWith(networkFirst(request));return}}event.respondWith((async()=>{{const cache=await caches.open(CACHE),cached=await cache.match(request);const network=fetch(request).then(response=>{{if(response&&response.ok)cache.put(request,response.clone());return response}}).catch(()=>null);return cached||(await network)||Response.error()}})())}});\n'''
Path('sw.js').write_text(SW,encoding='utf-8')
reduced='''<style id="mf-reduced-motion">@media (prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}</style>'''
pwa_css='''<style id="mf-pwa-style">#mfOfflineStatus{position:fixed;left:50%;bottom:18px;transform:translateX(-50%);z-index:99999;padding:9px 12px;border:1px solid #6d5a36;border-radius:999px;background:#1a150d;color:#ffd27c;font:850 10px/1.2 system-ui;box-shadow:0 10px 30px #0007}#installMetaForge{position:fixed;right:18px;bottom:18px;z-index:99998;border:1px solid #4ddff3;border-radius:999px;background:#0c1a28;color:#5de9ff;padding:10px 13px;font:900 10px/1 system-ui;cursor:pointer;box-shadow:0 10px 30px #0007}</style>'''
def prefix_for(path):return '../'*len(path.parent.parts)
count=0
for path in ROOT.rglob('*.html'):
    if path.name=='offline.html' or '.git' in path.parts or '_site' in path.parts:continue
    text=path.read_text(encoding='utf-8');prefix=prefix_for(path)
    if 'rel="manifest"' not in text:text=text.replace('</head>',f'<link rel="manifest" href="{prefix}manifest.webmanifest">'+reduced+pwa_css+'</head>',1)
    elif 'id="mf-reduced-motion"' not in text:text=text.replace('</head>',reduced+pwa_css+'</head>',1)
    if 'id="mf-pwa-runtime"' not in text:
        banner='<div id="mfOfflineStatus" role="status" hidden>Sin conexión · mostrando contenido guardado cuando esté disponible</div>';install=''
        if path==Path('index.html'):install='<button id="installMetaForge" type="button" hidden>Instalar Meta Forge</button>'
        runtime=f'''<script id="mf-pwa-runtime">(()=>{{const banner=document.getElementById('mfOfflineStatus');function syncOnline(){{if(banner)banner.hidden=navigator.onLine}}window.addEventListener('online',syncOnline);window.addEventListener('offline',syncOnline);syncOnline();if('serviceWorker' in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('{prefix}sw.js').catch(()=>{{}}));const install=document.getElementById('installMetaForge');let promptEvent=null;window.addEventListener('beforeinstallprompt',e=>{{e.preventDefault();promptEvent=e;if(install)install.hidden=false}});if(install)install.addEventListener('click',async()=>{{if(!promptEvent)return;promptEvent.prompt();await promptEvent.userChoice;promptEvent=null;install.hidden=true}});window.addEventListener('appinstalled',()=>{{promptEvent=null;if(install)install.hidden=true}})}})();</script>'''
        text=text.replace('</body>',banner+install+runtime+'</body>',1)
    path.write_text(text,encoding='utf-8');count+=1
print(f'PWA shell built: build={build_sha[:12]}; version={version}; cache={cache_name}; html_pages={count}; core={len(core)}; explorer_offline=true; png_icons=192/512; navigation_query_cache=false; product_release_offline=true; ux_refinements_offline=true')

# Generate the repair utility only after normal pages received their PWA runtime.
# This intentionally leaves repair/index.html outside the service-worker registration shell.
import generate_cache_repair
