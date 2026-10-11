from pathlib import Path
import json, os, struct, sys

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
for p in ['sw.js','offline.html','manifest.webmanifest','privacy.html','assets/icon-192.png','assets/icon-512.png']:
    need(Path(p).exists(),f'Missing PWA artifact: {p}')
manifest={}
if Path('manifest.webmanifest').exists():
    try: manifest=json.loads(Path('manifest.webmanifest').read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f'Invalid manifest JSON: {exc}')
need(manifest.get('id')=='./','Manifest id must be ./')
need(manifest.get('scope')=='./','Manifest scope must be ./')
need(manifest.get('lang')=='es','Manifest lang must be es')
shortcuts=manifest.get('shortcuts',[])
need(len(shortcuts)==4,f'Manifest should expose 4 shortcuts, got {len(shortcuts)}')
need({x.get('url') for x in shortcuts}=={'./roster/','./compare/','./trends/','./my-meta/'},'Manifest shortcut routes mismatch')
icons=manifest.get('icons',[])
icon_map={x.get('src'):x for x in icons if isinstance(x,dict)}
need(icon_map.get('assets/icon-192.png',{}).get('sizes')=='192x192','Manifest 192 PNG icon declaration missing')
need(icon_map.get('assets/icon-512.png',{}).get('sizes')=='512x512','Manifest 512 PNG icon declaration missing')
need('maskable' in icon_map.get('assets/icon-512.png',{}).get('purpose',''),'Manifest 512 PNG is not maskable-ready')

def png_size(path):
    try:
        raw=Path(path).read_bytes()
        if raw[:8]!=b'\x89PNG\r\n\x1a\n' or raw[12:16]!=b'IHDR': return None
        return struct.unpack('>II',raw[16:24])
    except Exception: return None
need(png_size('assets/icon-192.png')==(192,192),f'Generated 192 PNG dimensions invalid: {png_size("assets/icon-192.png")}')
need(png_size('assets/icon-512.png')==(512,512),f'Generated 512 PNG dimensions invalid: {png_size("assets/icon-512.png")}')
sw=Path('sw.js').read_text(encoding='utf-8') if Path('sw.js').exists() else ''
for token,msg in [
    ('mf-shell-','Versioned PWA cache missing'),
    ("request.method!=='GET'",'Service worker GET guard missing'),
    ('url.origin!==self.location.origin','Service worker same-origin guard missing'),
    ("request.mode==='navigate'",'Navigation offline strategy missing'),
    ("url.pathname.includes('/data/')",'Live-data network-first strategy missing'),
    ("cache.match('./offline.html')",'Offline fallback missing'),
    ('self.skipWaiting()','Service worker skipWaiting missing'),
    ('self.clients.claim()','Service worker clients.claim missing'),
    ("k.startsWith('mf-shell-')&&k!==CACHE",'Old PWA cache cleanup missing'),
    ("'./assets/icon-192.png'",'192 PNG is not precached'),
    ("'./assets/icon-512.png'",'512 PNG is not precached'),
]: need(token in sw,msg)
sha=os.getenv('GITHUB_SHA')
if sha: need(sha[:12] in sw,'Service worker cache is not tied to current GITHUB_SHA')
core=[Path('index.html'),Path('roster/index.html'),Path('trends/index.html'),Path('compare/index.html'),Path('my-meta/index.html'),Path('methodology.html'),Path('privacy.html'),Path('terms.html')]
for p in core:
    if not p.exists(): errors.append(f'Missing core PWA page: {p}'); continue
    t=p.read_text(encoding='utf-8')
    need('rel="manifest"' in t,f'Manifest link missing on {p}')
    need('id="mf-pwa-runtime"' in t,f'PWA runtime missing on {p}')
    need('id="mfOfflineStatus"' in t,f'Offline status missing on {p}')
    need('id="mf-reduced-motion"' in t,f'Reduced-motion support missing on {p}')
stat_pages=list(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []
need(len(stat_pages)==133,f'Expected 133 live hero pages, got {len(stat_pages)}')
covered=sum(1 for p in stat_pages if 'id="mf-pwa-runtime"' in p.read_text(encoding='utf-8') and 'rel="manifest"' in p.read_text(encoding='utf-8'))
need(covered==133,f'PWA runtime/manifest present on only {covered}/133 live hero pages')
home=Path('index.html').read_text(encoding='utf-8') if Path('index.html').exists() else ''
need('id="installMetaForge"' in home,'Homepage PWA install control missing')
need('beforeinstallprompt' in home,'Homepage PWA install-event handling missing')
privacy=Path('privacy.html').read_text(encoding='utf-8') if Path('privacy.html').exists() else ''
need('Cache Storage' in privacy and 'service worker' in privacy,'Privacy page does not disclose offline cache/service worker')
need('comparaciones recientes' in privacy,'Privacy page does not disclose recent compare history')
if errors:
    print('PWA VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'PWA validation passed: PNG icons=192/512, manifest shortcuts=4; live hero coverage={covered}/133; versioned offline shell, local cache disclosure and reduced-motion support present.')
