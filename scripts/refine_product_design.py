"""Apply the shared product design after all content generators, before PWA/SEO."""
from pathlib import Path
import datetime, html, json, os, re, unicodedata

HOME=Path('index.html')
page=HOME.read_text(encoding='utf-8')
if 'id="forgeHero"' in page:
    raise RuntimeError('Product design must run once on a fresh generated site')
live=json.loads(Path('data/live-meta.json').read_text())
heroes=live['heroes']
editorial=json.loads(Path('data/hero-catalog.json').read_text())['heroes']
esc=lambda value: html.escape(str(value),quote=True)
def slug(name):
    value=''.join(c for c in unicodedata.normalize('NFD',name.lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',value.replace('&','and')).strip('-')
def element_range(text,tag,marker):
    start=text.index(marker)
    depth=0
    for m in re.finditer(r'</?'+tag+r'\b[^>]*>',text[start:],re.I):
        depth+=-1 if m.group().startswith('</') else 1
        if depth==0:return start,start+m.end()
    raise RuntimeError(f'Unclosed {marker}')
def pop_element(tag,marker):
    global page
    start,end=element_range(page,tag,marker)
    value=page[start:end];page=page[:start]+page[end:]
    return value
health=pop_element('div','<div id="dataHealth"')
measured=live.get('source_updated')
if not measured:raise RuntimeError('A source date is required for the homepage snapshot')
date=datetime.datetime.fromisoformat(measured.replace('Z','+00:00')).strftime('%d/%m/%Y')
leaders=[]
for metric,label in [('wr','Mayor win rate'),('ban','Mayor ban rate'),('pick','Mayor pick rate')]:
    leader=sorted(heroes,key=lambda h:(-h[metric],h['name']))[0]
    name=esc(leader['name']);initial=esc(leader['name'][:2].upper())
    leaders.append(f'<a class="forge-leader" data-signal="{metric}" data-hero-key="{esc(leader["key"])}" href="stats/heroes/{slug(leader["name"])}/"><span class="forge-initial" aria-hidden="true">{initial}</span><span><small>{label}</small><b>{name}</b></span><strong>{leader[metric]:.2f}%</strong></a>')
hero=f'''<header id="forgeHero" class="hero-header"><div class="forge-hero-grid"><div class="forge-intro"><span class="badge">INTELIGENCIA DE META · PATCH {esc(live.get('patch','—'))}</span><h1>Lee el meta.<br><b>Prepara tu partida.</b></h1><p>Win rate, ban rate, pick rate y Meta Score para {len(heroes)} héroes de MLBB, con contexto de draft, fuente y fecha visibles. Encuentra qué está fuerte y conviértelo en una decisión útil.</p><div class="forge-ctas"><a class="forge-cta-main" href="roster/">Explorar héroes <span aria-hidden="true">↗</span></a><a class="forge-cta-alt" href="explore/">Abrir Meta Explorer <span aria-hidden="true">→</span></a></div><button class="forge-profile-action" type="button" data-open-profile>☆ Personalizar mi meta</button></div><aside class="forge-snapshot" aria-labelledby="forgeSnapshotTitle"><div class="forge-snapshot-head"><h2 id="forgeSnapshotTitle">En este snapshot</h2><span>3 SEÑALES</span></div>{''.join(leaders)}<p class="forge-source">Medición del proveedor: <time datetime="{esc(measured)}">{date}</time>.<br>Valores descriptivos; no son recomendaciones de pick.</p></aside></div><div class="forge-metrics"><span><b>{len(heroes)}</b> héroes con estadísticas</span><span><b id="heroCount">{len(editorial)}</b> perfiles editoriales</span><span>Patch <b id="patchKpi">{esc(live.get('patch','—'))}</b></span><span>Proyecto fan independiente</span></div></header>'''
start,end=element_range(page,'header','<header class="hero-header"')
page=page[:start]+hero+f'<details id="forgeDataDetails" class="forge-data-details"><summary>Fuente, fecha y estado de los datos</summary>{health}<button id="refresh" type="button">Consultar el snapshot</button></details>'+page[end:]
# Keep existing runtime IDs while putting secondary panels inside the Meta view.
sections=[pop_element('section',f'<section id="{key}"') for key in ['personalProfile','watchlistPanel','watchlistPulse','metaChanges','trendSpotlight']]
start,end=element_range(page,'section','<section id="heroes"')
extra='<details id="forgeMoreSignals" class="forge-more-signals"><summary>Tu seguimiento y cambios del meta</summary>'+''.join(sections)+'</details>'
page=page[:end-len('</section>')]+extra+page[end-len('</section>'):]
# Remove an empty advertising placeholder from the usable content.
page=re.sub(r'<div class="ad-slot">.*?</div>','',page,flags=re.S)
page=page.replace('Héroes que están pegando fuerte','El pool editorial, a detalle').replace('RANKED SNAPSHOT','ANÁLISIS EDITORIAL')
page=page.replace('>Alineaciones</button>','>Draft Lab</button>').replace('>Pro Tips</button>','>Consejos</button>')
page=page.replace('<div class="status"><i></i> Snapshot verificado · S42</div>','')
page=page.replace('<meta name="description" content="MLBB Meta Forge: snapshot editorial de héroes meta, alineaciones y consejos de draft para Mobile Legends: Bang Bang.">','<meta name="description" content="Explora 133 héroes de MLBB, compara estadísticas y prepara tu draft. Meta Explorer, seguimiento personal y análisis editorial con fuente y fecha visibles.">')
footer='''<footer><div><strong>MLBB Meta Forge</strong><span> · proyecto fan independiente para análisis de meta y draft.</span></div><div class="footer-links"><a href="methodology.html">Metodología</a><a href="privacy.html">Privacidad</a><a href="terms.html">Términos</a><a href="https://github.com/juanggm04-ship-it/mlbb-meta-forge" target="_blank" rel="noopener noreferrer">GitHub</a><a href="https://github.com/juanggm04-ship-it/mlbb-meta-forge/issues" target="_blank" rel="noopener noreferrer">Reportar problema</a></div></footer>'''
page=re.sub(r'<footer>.*?</footer>',footer,page,count=1,flags=re.S)
HOME.write_text(page,encoding='utf-8')

# Reuse cached stylesheets, add page identity for targeted responsive behavior and keep search in the navigation flow.
paths=[HOME,Path('roster/index.html'),Path('explore/index.html'),Path('trends/index.html'),Path('compare/index.html'),Path('my-meta/index.html'),Path('methodology.html')]+sorted(Path('stats/heroes').glob('*/index.html'))
page_keys={
    Path('index.html'):'home',
    Path('roster/index.html'):'roster',
    Path('explore/index.html'):'explorer',
    Path('trends/index.html'):'trends',
    Path('compare/index.html'):'compare',
    Path('my-meta/index.html'):'my-meta',
    Path('methodology.html'):'methodology',
}
for path in paths:
    text=path.read_text(encoding='utf-8')
    href=os.path.relpath('assets/product-design.css',path.parent).replace(os.sep,'/')
    ux_href=os.path.relpath('assets/ux-refinements.css',path.parent).replace(os.sep,'/')
    page_key=page_keys.get(path,'hero')
    text=re.sub(r'<body\b', f'<body data-mf-design="2" data-mf-page="{page_key}"',text,count=1)
    text=text.replace('</head>',f'<link rel="stylesheet" href="{href}" id="mf-product-design"><link rel="stylesheet" href="{ux_href}" id="mf-ux-refinements"></head>',1)
    if path==Path('explore/index.html') and 'id="explorerMobileHint"' not in text:
        marker='<div id="exploreDetail"'
        hint='<p id="explorerMobileHint" class="explorer-mobile-hint">En pantallas pequeñas, desliza el mapa horizontalmente para separar mejor los puntos.</p>'
        if marker not in text:raise RuntimeError('Explorer detail marker missing for mobile hint')
        text=text.replace(marker,hint+marker,1)
    match=re.search(r'<button\b[^>]*class="ghs-launch"[^>]*>.*?</button>',text,re.S)
    if match:
        launcher=match.group();text=text[:match.start()]+text[match.end():]
        if path==HOME:
            _,end=element_range(text,'div','<div class="topbar"')
            text=text[:end-6]+launcher+text[end-6:]
        else:
            _,end=element_range(text,'nav','<nav id="productShellNav"')
            text=text[:end-6]+launcher+text[end-6:]
    path.write_text(text,encoding='utf-8')
print(f'Product design refined: {len(paths)} pages; canonical snapshot leaders; responsive directory; page-aware UX layer; stronger value proposition; trust footer; optional profile; secondary panels grouped')
