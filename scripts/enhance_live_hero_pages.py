from pathlib import Path
from urllib.parse import quote
import json, re, html
from hero_identity import hero_key

LIVE=Path('data/live-meta.json')
SCORE=Path('data/meta-score.json')
CATALOG=Path('data/hero-catalog.json')
ROOT=Path('stats/heroes')

for p in [LIVE,SCORE,CATALOG]:
    if not p.exists():
        raise RuntimeError(f'Missing live hero product dependency: {p}')
if not ROOT.exists():
    raise RuntimeError('stats/heroes is required')

live=json.loads(LIVE.read_text(encoding='utf-8'))
score=json.loads(SCORE.read_text(encoding='utf-8'))
catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
heroes=live.get('heroes',[])
scores=score.get('heroes',[])
editorial_rows=catalog.get('heroes',[])
if len(heroes)!=133 or len(scores)!=133:
    raise RuntimeError(f'Hero product pages require 133 live/score rows; got live={len(heroes)} score={len(scores)}')
if len(editorial_rows)!=34:
    raise RuntimeError(f'Expected 34 editorial catalog rows, got {len(editorial_rows)}')

live_by={hero_key(h['name']):h for h in heroes if h.get('name')}
score_by={hero_key(h['name']):h for h in scores if h.get('name')}
editorial={hero_key(h['name']) for h in editorial_rows if h.get('name')}

CSS='''<style id="hero-product-page-style">
body{padding:0 18px 30px!important}.product-shell-nav{margin-top:14px}.hero{position:relative;overflow:hidden;background:radial-gradient(circle at 92% 10%,#2e205166 0,transparent 32%),linear-gradient(145deg,#0d1728,#0a101b 72%)!important;border-color:#304564!important}.hero:after{content:"";position:absolute;width:240px;height:240px;border-radius:50%;right:-105px;bottom:-125px;background:radial-gradient(circle,#53e6ff20,transparent 68%);pointer-events:none}.hero h1{margin-bottom:8px}.hero-product-summary{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap;margin:16px 0 4px;position:relative;z-index:1}.hero-product-score,.hero-product-rank,.hero-product-coverage{border:1px solid #304561;border-radius:16px;background:#08111dcc;padding:12px 14px;min-width:128px}.hero-product-score strong{display:block;font-size:30px;line-height:1;color:#cbb8ff}.hero-product-score span,.hero-product-rank span,.hero-product-coverage span{display:block;margin-top:4px;color:#7387a5;font-size:9px;font-weight:900;letter-spacing:.09em}.hero-product-rank b,.hero-product-coverage b{display:block;font-size:14px;color:#dce8f8}.hero-product-coverage.editorial b{color:#ffd36c}.hero-product-help{display:flex;align-items:center;margin-left:auto;padding:0 4px}.hero-product-help a{font-size:10px;color:#8195b2}.hero-quick-actions{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin-top:18px;position:relative;z-index:2}.hero-quick-actions a,.hero-quick-actions button{display:flex;justify-content:center;align-items:center;min-height:43px;padding:10px;border:1px solid #2c405d;border-radius:12px;background:#0c1625;color:#d8e5f7;text-decoration:none;font:850 11px/1.2 system-ui;text-align:center;cursor:pointer}.hero-quick-actions a:hover,.hero-quick-actions button:hover,.hero-quick-actions a:focus-visible,.hero-quick-actions button:focus-visible{border-color:#55dffb;outline:none;background:#102035}.hero-quick-actions .primary-action{background:linear-gradient(135deg,#4de5ff,#8b70ff);color:#07101b;border:0}.hero-quick-actions .watch-action.active{background:#52e3ff;color:#07101b;border-color:#52e3ff}.hero-quick-actions .editorial-action{border-color:#806635;color:#ffd77c;background:#17130b}.live-watch-wrap{display:none!important}a[data-hero-compare]{display:none!important}main>a:first-child{display:none}.hero-source{border:1px solid #263650;background:#0a111d;border-radius:18px;margin-top:18px;color:#9eacc4}.hero-source summary{cursor:pointer;padding:15px 17px;color:#aebdd2;font-size:11px;font-weight:900;letter-spacing:.06em;list-style:none}.hero-source summary::-webkit-details-marker{display:none}.hero-source summary:after{content:"＋";float:right;color:#5bdff7}.hero-source[open] summary:after{content:"−"}.hero-source-body{padding:0 18px 18px}.hero-source-body p{margin-top:0}.hero-source-body .actions{margin-top:12px}.hero-source-body h2{font-size:16px}.hero-ms{margin-top:14px!important}@media(max-width:760px){.hero-quick-actions{grid-template-columns:1fr 1fr}.hero-product-help{width:100%;margin-left:0}.hero-product-score,.hero-product-rank,.hero-product-coverage{flex:1}.hero-quick-actions .primary-action{grid-column:span 2}}@media(max-width:420px){body{padding-left:10px!important;padding-right:10px!important}.hero-product-summary{display:grid;grid-template-columns:1fr 1fr}.hero-product-coverage{grid-column:span 2}}
</style>'''

JS='''<script id="hero-product-page-script">(()=>{const proxy=document.getElementById('heroQuickWatch'),source=document.getElementById('liveWatchToggle');if(!proxy||!source)return;function sync(){const on=source.getAttribute('aria-pressed')==='true';proxy.classList.toggle('active',on);proxy.textContent=on?'★ Siguiendo':'☆ Seguir';proxy.setAttribute('aria-pressed',on?'true':'false')}proxy.addEventListener('click',()=>{source.click();requestAnimationFrame(sync)});new MutationObserver(sync).observe(source,{attributes:true,attributeFilter:['aria-pressed']});window.addEventListener('storage',sync);sync()})();</script>'''

pages=sorted(ROOT.glob('*/index.html'))
if len(pages)!=133:
    raise RuntimeError(f'Expected 133 live-stat pages, found {len(pages)}')

changed=0
editorial_count=0
for page in pages:
    text=page.read_text(encoding='utf-8')
    if 'id="heroProductSummary"' in text:
        continue
    m=re.search(r'<h1>(.*?)</h1>',text,re.S)
    if not m:
        raise RuntimeError(f'Hero heading missing in {page}')
    name=html.unescape(re.sub(r'<.*?>','',m.group(1))).strip()
    key=hero_key(name)
    live_row=live_by.get(key)
    score_row=score_by.get(key)
    if not live_row or not score_row:
        raise RuntimeError(f'Could not resolve live/score row for {name}')
    has_editorial=key in editorial
    if has_editorial: editorial_count+=1
    score_value=float(score_row['score'])
    rank=int(score_row['rank'])
    label=html.escape(str(score_row.get('label') or 'Señal estadística'))
    coverage=('EDITORIAL + LIVE' if has_editorial else 'LIVE STATS')
    summary=(f'<div id="heroProductSummary" class="hero-product-summary" data-hero-name="{html.escape(name,quote=True)}" data-meta-score="{score_value:.1f}" data-meta-rank="{rank}" data-editorial="{"true" if has_editorial else "false"}">'
             f'<div class="hero-product-score"><strong>{score_value:.1f}</strong><span>META SCORE · NO TIER</span></div>'
             f'<div class="hero-product-rank"><b>#{rank} de {len(heroes)}</b><span>{label}</span></div>'
             f'<div class="hero-product-coverage {"editorial" if has_editorial else ""}"><b>{coverage}</b><span>COBERTURA DE ESTA FICHA</span></div>'
             f'<div class="hero-product-help"><a href="../../../methodology.html#meta-score">Cómo se calcula →</a></div></div>')
    text=text.replace(m.group(0),m.group(0)+summary,1)

    editorial_action=(f'<a class="editorial-action" href="../../../heroes/{page.parent.name}/">Análisis editorial</a>' if has_editorial else '')
    actions=(f'<nav id="heroQuickActions" class="hero-quick-actions" aria-label="Acciones rápidas de {html.escape(name,quote=True)}">'
             f'<a href="../../../roster/">← Roster</a>'
             f'<a class="primary-action" href="../../../compare/?a={quote(name,safe="")}">⚔ Comparar</a>'
             f'<button id="heroQuickWatch" class="watch-action" type="button" aria-pressed="false">☆ Seguir</button>'
             f'<a href="../../../trends/">↗ Trends</a>'
             f'<a href="../../../my-meta/">★ Mi Meta</a>'
             f'{editorial_action}</nav>')
    # Put actions at the end of the hero header section, before downstream analysis blocks.
    hero_start=text.find('<section class="hero">')
    if hero_start==-1:
        raise RuntimeError(f'Hero section missing in {page}')
    hero_end=text.find('</section>',hero_start)
    if hero_end==-1:
        raise RuntimeError(f'Hero section closing tag missing in {page}')
    text=text[:hero_end]+actions+text[hero_end:]

    # Collapse the legacy provenance panel into a detail view; keep its content and links intact.
    marker='<section class="panel"><h2>Procedencia</h2>'
    if marker not in text:
        raise RuntimeError(f'Legacy provenance panel missing in {page}')
    text=text.replace(marker,'<details id="heroSourceDetails" class="hero-source"><summary>Procedencia y calidad del dato</summary><div class="hero-source-body"><h2>Procedencia</h2>',1)
    tail='</section></main>'
    if tail not in text:
        raise RuntimeError(f'Could not locate provenance panel tail in {page}')
    text=text.replace(tail,'</div></details></main>',1)

    text=text.replace('</head>',CSS+'</head>',1)
    text=text.replace('</body>',JS+'</body>',1)
    page.write_text(text,encoding='utf-8')
    changed+=1

if changed not in (0,len(pages)):
    raise RuntimeError(f'Enhanced only {changed}/{len(pages)} live hero pages')
if editorial_count!=34:
    raise RuntimeError(f'Expected 34 editorial hero product pages, matched {editorial_count}')
print(f'Live hero product pages ready: pages={len(pages)}; editorial={editorial_count}; stats_only={len(pages)-editorial_count}')
