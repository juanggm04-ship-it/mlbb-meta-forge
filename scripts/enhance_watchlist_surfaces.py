from pathlib import Path
import re

# Enhance trends page
tr=Path('trends/index.html')
if tr.exists():
    html=tr.read_text(encoding='utf-8')
    if 'mf-watch-toggle' not in html:
        css='''<style>.mf-watch-toggle{border:1px solid #33445f;background:#111a2c;color:#dce7f8;border-radius:9px;padding:7px 9px;cursor:pointer;font-size:11px}.mf-watch-toggle.active{background:#46e6ff;color:#07101b;border-color:#46e6ff}</style>'''
        html=html.replace('</head>',css+'</head>')
        js=r'''<script>
(()=>{
const KEY='mf_watchlist_v1';const get=()=>{try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch{return []}};const set=v=>localStorage.setItem(KEY,JSON.stringify([...new Set(v)]));
function sync(){document.querySelectorAll('[data-watch-hero]').forEach(b=>{const on=get().includes(b.dataset.watchHero);b.classList.toggle('active',on);b.textContent=on?'★ Siguiendo':'☆ Seguir'})}
document.addEventListener('click',e=>{const b=e.target.closest('[data-watch-hero]');if(!b)return;const n=b.dataset.watchHero;const list=get();set(list.includes(n)?list.filter(x=>x!==n):[...list,n]);sync()});
const obs=new MutationObserver(sync);obs.observe(document.body,{childList:true,subtree:true});sync();
})();
</script>'''
        html=html.replace('</body>',js+'</body>')
        # inject watch button into trend rows/cards by replacing detail links when possible
        html=html.replace('>Ver ficha →</a>', '>Ver ficha →</a> <button class="mf-watch-toggle" type="button" data-watch-hero="${h.name}">☆ Seguir</button>')
        tr.write_text(html,encoding='utf-8')

# Enhance hero pages
for page in Path('heroes').glob('*/index.html'):
    if page.parent.name=='index.html':
        continue
    html=page.read_text(encoding='utf-8')
    if 'id="heroWatchToggle"' in html:
        continue
    m=re.search(r'<h1>(.*?)</h1>',html,re.S)
    if not m: continue
    name=re.sub('<.*?>','',m.group(1)).strip()
    btn=f'<button id="heroWatchToggle" class="cta" type="button" data-hero-name="{name}">☆ Seguir héroe</button>'
    html=html.replace('</section><section class="box"><h2>Lectura del snapshot</h2>',btn+'</section><section class="box"><h2>Lectura del snapshot</h2>',1)
    js=r'''<script>
(()=>{
const b=document.getElementById('heroWatchToggle');if(!b)return;const KEY='mf_watchlist_v1',name=b.dataset.heroName;const get=()=>{try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch{return []}};const set=v=>localStorage.setItem(KEY,JSON.stringify([...new Set(v)]));function sync(){const on=get().includes(name);b.textContent=on?'★ Siguiendo':'☆ Seguir héroe'}b.onclick=()=>{const l=get();set(l.includes(name)?l.filter(x=>x!==name):[...l,name]);sync()};sync();
})();
</script>'''
    html=html.replace('</body>',js+'</body>')
    page.write_text(html,encoding='utf-8')

print('Enhanced Trends and hero pages with watchlist controls')
