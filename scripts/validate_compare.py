from pathlib import Path
import sys

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

compare=Path('compare/index.html')
need(compare.exists(),'Hero Compare page missing')
if compare.exists():
    text=compare.read_text(encoding='utf-8')
    for token in ['id="a"','id="b"','Meta Score','Momentum','Ranking','URLSearchParams','searchParams.set(\'a\'','searchParams.set(\'b\'','Copiar enlace','id="swapHeroes"','Por qué cambia el Meta Score','Percentil WR','Percentil Pick','Percentil Ban','Percentil Momentum','avoidSame']:
        need(token in text,f'Hero Compare missing: {token}')

stat_pages=list(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []
need(len(stat_pages)>=100,f'Only {len(stat_pages)} live-stat pages found for compare validation')
with_cta=sum(1 for p in stat_pages if 'data-hero-compare' in p.read_text(encoding='utf-8'))
need(with_cta==len(stat_pages),f'Compare CTA present on only {with_cta}/{len(stat_pages)} live-stat pages')

roster=Path('roster/index.html')
need(roster.exists(),'Live Roster missing')
if roster.exists():need('href="../compare/"' in roster.read_text(encoding='utf-8'),'Live Roster has no Hero Compare entry')

my_meta=Path('my-meta/index.html')
need(my_meta.exists(),'My Meta missing')
if my_meta.exists():
    text=my_meta.read_text(encoding='utf-8')
    need('id="myMetaCompare"' in text,'My Meta Watchlist compare panel missing')
    need('id="mmcA"' in text and 'id="mmcB"' in text,'My Meta compare selectors missing')
    need("new URL('../compare/'" in text,'My Meta compare routing missing')

sitemap=Path('sitemap.xml')
need(sitemap.exists(),'Sitemap missing')
if sitemap.exists():need('/compare/' in sitemap.read_text(encoding='utf-8'),'Sitemap missing /compare/')

src=Path('scripts/generate_hero_compare.py').read_text(encoding='utf-8')
need("params.get('a')" in src and "params.get('b')" in src,'Compare URL parameter restore logic missing')
need("history.replaceState" in src,'Compare shareable URL update logic missing')
need('quote(name,safe="")' in src,'Per-hero compare links are not URL encoded')

enhance=Path('scripts/enhance_hero_compare.py').read_text(encoding='utf-8')
need("metric('Percentil WR'" in enhance and "metric('Percentil Pick'" in enhance and "metric('Percentil Ban'" in enhance and "metric('Percentil Momentum'" in enhance,'Compare score component explanation source incomplete')
need("swapHeroes" in enhance and "avoidSame" in enhance,'Compare swap/distinct-selection logic missing')

if errors:
    print('HERO COMPARE VALIDATION FAILED')
    for e in errors:print('- '+e)
    sys.exit(1)
print(f'Hero Compare validation passed: page present, {with_cta}/{len(stat_pages)} stat CTAs, component explanation, swap/distinct selection, My Meta Watchlist compare, shareable a/b parameters and sitemap entry present.')
