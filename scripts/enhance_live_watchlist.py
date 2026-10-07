from pathlib import Path
import re, html as htmlmod

pages=sorted(Path('stats/heroes').glob('*/index.html'))
if len(pages)<100:
    raise RuntimeError(f'Expected at least 100 live-stat hero pages, found {len(pages)}')

CSS='''<style id="live-watch-style">.live-watch-wrap{display:flex;gap:9px;flex-wrap:wrap;margin-top:14px}.live-watch-btn{display:inline-flex;align-items:center;padding:10px 13px;border:1px solid #35506d;border-radius:12px;background:#101b2c;color:#e4efff;font:800 12px/1 system-ui;cursor:pointer}.live-watch-btn.active{background:#49e4ff;color:#06101a;border-color:#49e4ff}.live-watch-link{display:inline-flex;align-items:center;padding:10px 13px;border:1px solid #30415d;border-radius:12px;background:#0d1625;color:#b9c9df;font:800 12px/1 system-ui;text-decoration:none}</style>'''

JS=r'''<script id="live-watch-script">(()=>{const KEY='mf_watchlist_v1',b=document.getElementById('liveWatchToggle');if(!b)return;const name=b.dataset.heroName;const get=()=>{try{const v=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(v)?v:[]}catch{return []}};const set=v=>localStorage.setItem(KEY,JSON.stringify([...new Set(v)]));function sync(){const on=get().includes(name);b.classList.toggle('active',on);b.textContent=on?'★ Siguiendo':'☆ Seguir héroe';b.setAttribute('aria-pressed',on?'true':'false')}b.addEventListener('click',()=>{const v=get();set(v.includes(name)?v.filter(x=>x!==name):[...v,name]);sync()});window.addEventListener('storage',sync);sync()})();</script>'''

changed=0
for page in pages:
    src=page.read_text(encoding='utf-8')
    if 'id="liveWatchToggle"' in src:
        continue
    m=re.search(r'<h1>(.*?)</h1>',src,re.S)
    if not m:
        raise RuntimeError(f'Could not find hero heading in {page}')
    name=htmlmod.unescape(re.sub(r'<.*?>','',m.group(1))).strip()
    safe=htmlmod.escape(name,quote=True)
    controls=f'''<div class="live-watch-wrap"><button id="liveWatchToggle" class="live-watch-btn" type="button" aria-pressed="false" data-hero-name="{safe}">☆ Seguir héroe</button><a class="live-watch-link" href="../../../my-meta/">Abrir Mi Meta →</a></div>'''
    if '</head>' in src: src=src.replace('</head>',CSS+'</head>',1)
    # Prefer the hero section; fall back to first panel.
    needle='</section><section class="panel">'
    if needle in src: src=src.replace(needle,controls+needle,1)
    else: src=src.replace('</main>',controls+'</main>',1)
    src=src.replace('</body>',JS+'</body>',1)
    page.write_text(src,encoding='utf-8');changed+=1

# Add a concise hint/shortcut on the roster page.
roster=Path('roster/index.html')
if roster.exists():
    src=roster.read_text(encoding='utf-8')
    if 'watchlist-hint' not in src:
        hint='<div id="watchlist-hint" class="meta"><a class="pill editorial" href="../my-meta/">★ Mi Meta</a><span class="pill live">Abre una ficha live para seguir cualquier héroe</span></div>'
        marker='</section><div class="toolbar">'
        if marker in src:src=src.replace(marker,'</section>'+hint+'<div class="toolbar">',1)
        roster.write_text(src,encoding='utf-8')

print(f'Added live Watchlist controls to {len(pages)} statistical hero pages; changed={changed}')