from pathlib import Path
import json,re,sys
from hero_identity import hero_key

PAGE=Path('explore/index.html')
LIVE=Path('data/live-meta.json')
SCORE=Path('data/meta-score.json')
CATALOG=Path('data/hero-catalog.json')
SITEMAP=Path('sitemap.xml')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
for p in (PAGE,LIVE,SCORE,CATALOG,SITEMAP): need(p.exists(),f'Missing Meta Explorer dependency: {p}')
if not errors:
    page=PAGE.read_text(encoding='utf-8')
    live=json.loads(LIVE.read_text(encoding='utf-8'))
    score=json.loads(SCORE.read_text(encoding='utf-8'))
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    heroes=[h for h in live.get('heroes',[]) if h.get('name')]
    scores={hero_key(h.get('name')):h for h in score.get('heroes',[]) if h.get('name')}
    editorial={hero_key(h.get('name')) for h in catalog.get('heroes',[]) if h.get('name')}
    need(len(heroes)==133,f'Expected 133 live heroes, got {len(heroes)}')
    need(len(scores)==133,f'Expected 133 Meta Score rows, got {len(scores)}')
    need(len(editorial)==34,f'Expected 34 editorial identities, got {len(editorial)}')
    for token,msg in [
        ('id="metaPlot"','Explorer SVG missing'),
        ('id="exploreSearch"','Explorer search missing'),
        ('id="xMetric"','X metric selector missing'),
        ('id="yMetric"','Y metric selector missing'),
        ('id="copyExplorer"','Share-view control missing'),
        ('id="exploreDetail"','Selected-hero detail missing'),
        ('id="meta-explorer-runtime"','Explorer runtime missing'),
        ('X bajo · Y alto','Descriptive quadrant labels missing'),
        ('No son tiers, roles, counters ni probabilidades de victoria.','Statistical disclaimer missing'),
        ('Tabla accesible · 133 héroes','Accessible table disclosure missing'),
        ('history.replaceState','Shareable explorer state missing'),
        ("u.searchParams.set('x',xs.value)",'X-axis URL state missing'),
        ("u.searchParams.set('y',ys.value)",'Y-axis URL state missing'),
        ("u.searchParams.set('hero',selected.name)",'Selected hero URL state missing'),
        ('../compare/?a=${encodeURIComponent(h.name)}','Compare handoff missing'),
        ('../stats/heroes/${h.slug}/','Stat-page handoff missing'),
    ]: need(token in page,msg)
    need(page.count('<tr data-key=')==133,f'Accessible table must contain 133 hero rows, got {page.count("<tr data-key=")}')
    embedded=re.search(r'const HEROES=(\[.*?\]);const metrics=',page,re.S)
    need(bool(embedded),'Embedded Explorer hero dataset missing')
    if embedded:
        try: rows=json.loads(embedded.group(1))
        except Exception as exc: rows=[];errors.append(f'Explorer embedded hero JSON invalid: {exc}')
        need(len(rows)==133,f'Explorer embedded dataset must contain 133 heroes, got {len(rows)}')
        if rows:
            by={hero_key(r.get('name')):r for r in rows}
            need(len(by)==133,'Explorer embedded hero identities are not unique')
            need(sum(1 for r in rows if r.get('editorial'))==34,'Explorer editorial flag count must be 34')
            for h in heroes:
                k=hero_key(h['name']);r=by.get(k);s=scores.get(k)
                need(r is not None,f'Explorer missing hero {h["name"]}')
                if r and s:
                    for stat in ('wr','ban','pick'): need(r.get(stat)==h.get(stat),f'Explorer {h["name"]} {stat} mismatch')
                    need(r.get('score')==s.get('score'),f'Explorer {h["name"]} Meta Score mismatch')
                    need(r.get('rank')==s.get('rank'),f'Explorer {h["name"]} rank mismatch')
                    need(r.get('editorial')==(k in editorial),f'Explorer {h["name"]} editorial flag mismatch')
    need('https://juanggm04-ship-it.github.io/mlbb-meta-forge/explore/' in SITEMAP.read_text(encoding='utf-8'),'Explorer route missing from sitemap')
if errors:
    print('META EXPLORER VALIDATION FAILED')
    for e in errors[:80]: print('- '+e)
    if len(errors)>80: print(f'- ... and {len(errors)-80} more')
    sys.exit(1)
print('Meta Explorer validation passed: 133 live heroes, 34 editorial flags, four statistical metrics, shareable axes/selection, accessible table and exact source values.')
