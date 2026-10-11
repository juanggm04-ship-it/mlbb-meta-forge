from pathlib import Path
import json,re,sys

HOME=Path('index.html')
LIVE=Path('data/live-meta.json')
HISTORY=Path('data/meta-history.json')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

need(HOME.exists(),'Homepage missing')
need(LIVE.exists(),'live-meta.json missing')
need(HISTORY.exists(),'meta-history.json missing')

if HOME.exists() and LIVE.exists() and HISTORY.exists():
    html=HOME.read_text(encoding='utf-8')
    live=json.loads(LIVE.read_text(encoding='utf-8'))
    history=json.loads(HISTORY.read_text(encoding='utf-8'))
    hero_count=len(live.get('heroes',[]))
    snapshots=len(history.get('snapshots',[]))

    need('id="homeProductHub"' in html,'Homepage product hub missing')
    need(f'data-live-heroes="{hero_count}"' in html,'Homepage live hero count does not match snapshot')
    need(f'data-history-snapshots="{snapshots}"' in html,'Homepage history snapshot count does not match history')
    need(len(re.findall(r'class="home-launch-card(?: [^"]*)?"',html))==6,'Homepage must expose exactly six launch cards')

    for href,label in [('roster/','Live Roster'),('compare/','Hero Compare'),('trends/','Trends'),('my-meta/','My Meta')]:
        need(f'href="{href}"' in html,f'{label} route missing from homepage hub/navigation')
    need('data-go="drafts"' in html,'Draft Lab launch action missing')
    need(html.count('data-global-hero-search')>=3,'Search action is not exposed in hub/mobile/global launcher')

    need('<nav class="product-nav"' in html,'Desktop product navigation missing')
    need('class="mobile-dock home-mobile-dock"' in html,'Primary mobile dock missing')
    need('<a href="my-meta/">Mi Meta</a>' in html,'My Meta mobile destination missing')
    need('grid-template-columns:repeat(4,1fr)!important' in html,'Mobile dock four-destination layout missing')

    if snapshots < 2:
        need('1 snapshot real · esperando cambio real' in html,'Homepage Trends card must disclose one-snapshot waiting state')
        need('Esperando señal real' in html,'Homepage Trends card must avoid implying observed movement')
    else:
        need(f'{snapshots} snapshots reales · historial activo' in html,'Homepage Trends card active-history state mismatch')

    need('Seis rutas, una sola portada' in html,'Homepage hub orientation copy missing')
    need('Estadísticas live y análisis editorial siguen claramente separados' in html,'Homepage live/editorial distinction missing')

if errors:
    print('HOME PRODUCT HUB VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Homepage product hub validation passed: six primary routes, live/history state, desktop navigation and four-destination mobile dock are synchronized.')
