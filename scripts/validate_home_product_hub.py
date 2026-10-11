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
    need(len(re.findall(r'class="home-launch-card(?: [^"]*)?"',html))==7,'Homepage must expose exactly seven launch cards')
    need(len(re.findall(r'data-home-intent="[^"]+"',html))==3,'Homepage must expose exactly three first-run intent shortcuts')
    for token,label in [
        ('data-home-intent="strong"','strong-meta intent'),
        ('href="roster/?filter=top20"','Top 20 direct route'),
        ('data-home-intent="compare"','compare intent'),
        ('data-home-intent="draft"','draft intent'),
        ('¿Qué está fuerte?','plain-language strong-meta question'),
        ('¿Quién gana entre dos?','plain-language comparison question'),
        ('¿Qué pick preparo?','plain-language draft question')]:
        need(token in html,f'Homepage {label} missing')

    for href,label in [('roster/','Live Roster'),('explore/','Meta Explorer'),('compare/','Hero Compare'),('trends/','Trends'),('my-meta/','My Meta')]:
        need(f'href="{href}"' in html,f'{label} route missing from homepage hub/navigation')
    need(html.count('data-go="drafts"')>=2,'Draft Lab must be available from quick intent and full launch grid')
    need(html.count('data-global-hero-search')>=2,'Search action is not exposed in hub/global launcher')

    need('<nav class="product-nav"' in html,'Desktop product navigation missing')
    need('<a href="explore/">Explorer</a>' in html,'Explorer desktop route missing')
    need('class="mobile-dock home-mobile-dock"' in html,'Primary mobile dock missing')
    need('<a href="my-meta/">Mi Meta</a>' in html,'My Meta mobile destination missing')
    need('grid-template-columns:repeat(4,1fr)!important' in html,'Mobile dock four-destination layout missing')

    if snapshots < 2:
        need('1 snapshot real · esperando cambio real' in html,'Homepage Trends card must disclose one-snapshot waiting state')
        need('Esperando señal real' in html,'Homepage Trends card must avoid implying observed movement')
    else:
        need(f'{snapshots} snapshots reales · historial activo' in html,'Homepage Trends card active-history state mismatch')

    need('Empieza con una decisión rápida' in html,'Homepage decision-first orientation copy missing')
    need('siete herramientas completas de Meta Forge' in html,'Homepage full-tool fallback copy missing')
    need('WR, pick, ban y Meta Score en 133 puntos' in html,'Meta Explorer launch description missing')

if errors:
    print('HOME PRODUCT HUB VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Homepage product hub validation passed: three decision-first intents, seven full routes, live/history state, desktop navigation and four-destination mobile dock are synchronized.')
