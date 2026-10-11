from pathlib import Path
import json

HOME=Path('index.html')
LIVE=Path('data/live-meta.json')
HISTORY=Path('data/meta-history.json')

if not HOME.exists() or not LIVE.exists() or not HISTORY.exists():
    raise RuntimeError('Homepage, live meta and history are required')

html=HOME.read_text(encoding='utf-8')
if 'id="homeProductHub"' in html:
    print('Homepage product hub already present')
    raise SystemExit

live=json.loads(LIVE.read_text(encoding='utf-8'))
history=json.loads(HISTORY.read_text(encoding='utf-8'))
hero_count=len(live.get('heroes',[]))
snapshot_count=len(history.get('snapshots',[]))
if hero_count < 100:
    raise RuntimeError(f'Homepage product hub requires full live roster, found {hero_count}')

history_copy=(
    f'{snapshot_count} snapshots reales · historial activo'
    if snapshot_count >= 2 else
    '1 snapshot real · esperando cambio real'
    if snapshot_count == 1 else
    'Historial aún no disponible'
)

# Remove the older quick-action block from inside the hero. It has no nested divs.
marker='<div id="homeQuickActions" class="quick-actions">'
start=html.find(marker)
if start < 0:
    raise RuntimeError('Legacy homeQuickActions block missing')
end=html.find('</div>',start)
if end < 0:
    raise RuntimeError('Could not close legacy homeQuickActions block')
html=html[:start]+html[end+6:]

css='''<style id="home-product-hub-style">
.product-nav{display:flex;align-items:center;gap:4px;margin-left:auto}.product-nav a{padding:8px 10px;border-radius:10px;color:#8fa0bc;text-decoration:none;font-size:11px;font-weight:850}.product-nav a:hover,.product-nav a:focus-visible{background:#111b2d;color:#eff6ff;outline:none}.home-product-hub{width:min(1180px,calc(100% - 28px));margin:16px auto 0;padding:18px;border:1px solid #293a58;border-radius:24px;background:linear-gradient(145deg,#0b1423,#10172a)}.home-product-head{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:12px}.home-product-head small{color:#53e6ff;font-size:9px;font-weight:950;letter-spacing:.14em}.home-product-head h2{margin:4px 0 0;font-size:22px;letter-spacing:-.035em}.home-product-head p{margin:0;max-width:540px;color:#7f90ad;font-size:11px;line-height:1.5}.home-product-grid{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px}.home-launch-card{min-width:0;display:flex;flex-direction:column;min-height:132px;padding:13px;border:1px solid #263956;border-radius:15px;background:#091220;color:#eaf3ff;text-align:left;text-decoration:none;cursor:pointer;transition:.18s transform,.18s border-color,.18s background}.home-launch-card:hover,.home-launch-card:focus-visible{transform:translateY(-2px);border-color:#4edfff80;background:#0d192a;outline:none}.home-launch-card .home-launch-icon{font-size:20px;line-height:1}.home-launch-card small{margin-top:10px;color:#6f83a1;font-size:8px;font-weight:950;letter-spacing:.1em}.home-launch-card b{margin-top:4px;font-size:13px;line-height:1.2}.home-launch-card span{margin-top:6px;color:#7f91ad;font-size:10px;line-height:1.35}.home-launch-card em{margin-top:auto;padding-top:9px;color:#63e3ff;font-size:9px;font-style:normal;font-weight:850}.home-launch-card.primary-route{border-color:#36577b;background:linear-gradient(145deg,#0b1828,#12172b)}.home-launch-card.history-wait em{color:#ffd36c}.home-mobile-dock a{display:grid;place-items:center;text-decoration:none}.home-mobile-dock button,.home-mobile-dock a{border:0;background:#111a2c;color:#dbe7f8;border-radius:11px;padding:10px 6px;font-size:11px;font-weight:800}.home-mobile-dock a:focus-visible{outline:2px solid #46e6ff}.home-mobile-dock{grid-template-columns:repeat(4,1fr)!important}
@media(max-width:1000px){.home-product-grid{grid-template-columns:repeat(3,1fr)}.product-nav{display:none}}
@media(max-width:640px){.home-product-hub{padding:14px}.home-product-head{align-items:flex-start;flex-direction:column}.home-product-grid{display:flex;overflow:auto;scroll-snap-type:x mandatory;padding-bottom:4px}.home-launch-card{min-width:190px;scroll-snap-align:start}.home-product-head p{font-size:10px}}
</style>'''
html=html.replace('</head>',css+'</head>',1)

hub=f'''<section id="homeProductHub" class="home-product-hub" aria-label="Herramientas principales" data-live-heroes="{hero_count}" data-history-snapshots="{snapshot_count}"><div class="home-product-head"><div><small>EMPIEZA AQUÍ</small><h2>¿Qué quieres hacer?</h2></div><p>Seis rutas, una sola portada. Estadísticas live y análisis editorial siguen claramente separados.</p></div><div class="home-product-grid"><a class="home-launch-card primary-route" href="roster/"><span class="home-launch-icon">◉</span><small>LIVE ROSTER</small><b>Explorar el meta</b><span>{hero_count} héroes · WR, ban y pick</span><em>Abrir roster →</em></a><a class="home-launch-card" href="compare/"><span class="home-launch-icon">⚔</span><small>HERO COMPARE</small><b>Comparar 2 héroes</b><span>Stats, Meta Score y contexto editorial si existe</span><em>Comparar →</em></a><a class="home-launch-card {'history-wait' if snapshot_count < 2 else ''}" href="trends/"><span class="home-launch-icon">↗</span><small>TRENDS</small><b>Ver movimientos</b><span>{history_copy}</span><em>{'Esperando señal real' if snapshot_count < 2 else 'Abrir tendencias →'}</em></a><a class="home-launch-card" href="my-meta/"><span class="home-launch-icon">◎</span><small>MI META</small><b>Ver mi Watchlist</b><span>Ranking y señales de los héroes que sigues</span><em>Abrir Mi Meta →</em></a><button class="home-launch-card" type="button" data-go="drafts"><span class="home-launch-icon">◇</span><small>DRAFT LAB</small><b>Preparar un draft</b><span>Coach, 5v5 libre y Blue vs Red</span><em>Abrir Draft Lab ↓</em></button><button class="home-launch-card" type="button" data-global-hero-search><span class="home-launch-icon">⌕</span><small>BUSCADOR GLOBAL</small><b>Buscar un héroe</b><span>Encuentra cualquiera del roster live</span><em>Ctrl K · Buscar</em></button></div></section>'''
if '</header>' not in html:
    raise RuntimeError('Homepage hero header closing tag missing')
html=html.replace('</header>','</header>'+hub,1)

# Add compact desktop route navigation to the top bar.
if '<nav class="product-nav"' not in html:
    status_marker='<div class="status">'
    nav='<nav class="product-nav" aria-label="Herramientas"><a href="roster/">Roster</a><a href="trends/">Trends</a><a href="compare/">Comparar</a><a href="my-meta/">Mi Meta</a></nav>'
    if status_marker not in html:
        raise RuntimeError('Homepage status marker missing')
    html=html.replace(status_marker,nav+status_marker,1)

# Replace the old 3-tab mobile dock with four primary destinations.
old_mobile='<div class="mobile-dock" id="mobileDock"><button data-view-target="heroes">Meta</button><button data-view-target="drafts">Draft</button><button data-view-target="tips">Tips</button></div>'
new_mobile='<div class="mobile-dock home-mobile-dock" id="mobileDock"><button data-view-target="heroes">Meta</button><button data-view-target="drafts">Draft</button><button type="button" data-global-hero-search>Buscar</button><a href="my-meta/">Mi Meta</a></div>'
if old_mobile not in html:
    raise RuntimeError('Legacy mobile dock marker missing')
html=html.replace(old_mobile,new_mobile,1)

HOME.write_text(html,encoding='utf-8')
print(f'Homepage product hub ready: routes=6; live={hero_count}; snapshots={snapshot_count}; mobile=4 destinations')
