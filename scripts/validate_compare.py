from pathlib import Path
import sys

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

compare=Path('compare/index.html')
need(compare.exists(),'Hero Compare page missing')
if compare.exists():
    text=compare.read_text(encoding='utf-8')
    for token in ['id="a"','id="b"','Meta Score','Momentum','Ranking','URLSearchParams','searchParams.set(\'a\'','searchParams.set(\'b\'','Copiar enlace','id="swapHeroes"','Por qué cambia el Meta Score','Percentil WR','Percentil Pick','Percentil Ban','Percentil Momentum','avoidSame','id="compareEditorial"','EDITORIAL · SOLO SI AMBOS ESTÁN CURADOS','Frontline','Engage','Sustain','Peel','Waveclear','Scaling','Poke','Contexto editorial no disponible','id="compareMatchup"','INTERACCIÓN EDITORIAL','SIN REGLA DIRECTA','No es counter-rate ni probabilidad de victoria']:
        need(token in text,f'Hero Compare missing: {token}')
    need('puntos porcentuales' in text,'Hero Compare does not disclose WR/ban/pick percentage-point units')
    need('momentum_observed' in text,'Hero Compare payload does not expose momentum availability')
    need('neutral · esperando historial' in text or '· neutral' in text,'Hero Compare does not label unavailable momentum as neutral')
    need('No significa que el héroe no haya cambiado' in text,'Hero Compare neutral momentum explanation missing')

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
need("'momentum_observed':bool(s.get('momentum_observed'))" in src,'Compare source does not carry Meta Score momentum availability')
need('puntos porcentuales' in src,'Compare source does not explain raw live-stat rate units')

enhance=Path('scripts/enhance_hero_compare.py').read_text(encoding='utf-8')
need("metric('Percentil WR'" in enhance and "metric('Percentil Pick'" in enhance and "metric('Percentil Ban'" in enhance and "metric('Percentil Momentum'" in enhance,'Compare score component explanation source incomplete')
need("swapHeroes" in enhance and "avoidSame" in enhance,'Compare swap/distinct-selection logic missing')
need('momentumPercentile()' in enhance and 'momentum_observed' in enhance,'Compare does not use momentum availability when rendering components')
need('neutral-value' in enhance and 'Momentum neutral no es tendencia observada' in enhance,'Compare neutral momentum styling/disclosure missing')

editorial=Path('scripts/inject_compare_editorial.py').read_text(encoding='utf-8')
need("CORE=Path('data/editorial-core.json')" in editorial,'Compare editorial context is not sourced from shared editorial core')
need('renderEditorial(a,b)' in editorial,'Compare editorial render hook missing')
need("if(!pa||!pb)" in editorial,'Compare editorial missing-data guard missing')
need("editorialMetrics=[['front','Frontline']" in editorial,'Compare editorial capability map missing')

matchup=Path('scripts/inject_compare_matchup.py').read_text(encoding='utf-8')
need("CORE=Path('data/editorial-core.json')" in matchup,'Direct matchup context is not sourced from shared editorial core')
need("matchups=core.get('matchups',{})" in matchup,'Direct matchup context does not use shared matchup rules')
need('renderDirectMatchup(a,b)' in matchup,'Direct matchup render hook missing')
need("if((ar.good||[]).includes(b.name))" in matchup and "if((ar.warn||[]).includes(b.name))" in matchup,'Direct matchup good/warn interpretation missing')
need('No es counter-rate ni probabilidad de victoria' in matchup,'Direct matchup disclaimer missing')
need('SIN REGLA DIRECTA' in matchup,'Direct matchup neutral fallback missing')

if errors:
    print('HERO COMPARE VALIDATION FAILED')
    for e in errors:print('- '+e)
    sys.exit(1)
print(f'Hero Compare validation passed: page present, {with_cta}/{len(stat_pages)} stat CTAs, rate-unit disclosure, neutral/observed momentum semantics, score components, optional shared-core editorial context, direct matchup context, swap/distinct selection, My Meta Watchlist compare, shareable a/b parameters and sitemap entry present.')
