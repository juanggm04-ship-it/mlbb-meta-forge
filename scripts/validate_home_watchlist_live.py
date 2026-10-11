from pathlib import Path
import sys

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

src_path=Path('scripts/inject_watchlist.py')
index=Path('index.html')
need(src_path.exists(),'Homepage Watchlist injector missing')
need(index.exists(),'Homepage missing')

if src_path.exists():
    src=src_path.read_text(encoding='utf-8')
    for token in ["load('data/live-meta.json')","load('data/hero-catalog.json')","stats/heroes/${slug(name)}/","Análisis editorial →","const norm=n=>","has(name){const k=norm(name)"]:
        need(token in src,f'Homepage Watchlist source missing: {token}')
    need('href="heroes/${slug(name)}/">Ver tendencia' not in src,'Homepage Watchlist still routes every hero to editorial pages')

if index.exists():
    text=index.read_text(encoding='utf-8')
    for token in ['id="watchlistPanel"','Stats live →','Análisis editorial →',"load('data/hero-catalog.json')","stats/heroes/${slug(name)}/","const norm=n=>"]:
        need(token in text,f'Generated homepage Watchlist missing: {token}')

if errors:
    print('HOME WATCHLIST LIVE VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Homepage Watchlist validation passed: normalized live stats links for all followed heroes with editorial analysis only when catalog coverage exists.')
