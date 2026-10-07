from pathlib import Path
import json,re,sys

errors=[]

def need(cond,msg):
    if not cond: errors.append(msg)

def read(path):
    p=Path(path)
    need(p.exists(),f'Missing required file: {path}')
    return p.read_text(encoding='utf-8') if p.exists() else ''

html=read('index.html')
required_ids=[
    'homeQuickActions','draftLibrary','turnDraft','saveTurnDraft','postDraftAnalysis',
    'dataHealth','metaChanges','watchlistPanel','watchlistPulse','dataProvenance','globalHeroSearch'
]
for item in required_ids:
    need(f'id="{item}"' in html,f'Missing homepage module: #{item}')

need('LIVE STATS' in html and 'EDITORIAL' in html,'Homepage provenance labels missing')
need('trends/' in html,'Homepage has no link/reference to Trends')
need('my-meta/' in html,'Homepage has no link/reference to My Meta')
need('roster/' in html,'Homepage has no link/reference to Live Roster')
need('stats/heroes/' in html,'Homepage global search has no live-stat route')

trends=read('trends/index.html')
my_meta=read('my-meta/index.html')
need('<title>' in trends and 'Trend' in trends,'Trends page title missing')
need('<title>' in my_meta and ('Meta' in my_meta or 'meta' in my_meta),'My Meta page title missing')
need('id="dataProvenance"' in trends,'Trends provenance missing')
need('id="dataProvenance"' in my_meta,'My Meta provenance missing')
need('id="globalHeroSearch"' in trends,'Trends global hero search missing')
need('id="globalHeroSearch"' in my_meta,'My Meta global hero search missing')
need('stats/heroes/' in trends,'Trends has no live-stat route')
need('stats/heroes/' in my_meta,'My Meta global search has no live-stat route')
need('id="trendModeLive"' in trends,'Trends live mode toggle missing')
need('id="trendModeEditorial"' in trends,'Trends editorial mode toggle missing')
need('id="lane"' in trends and 'id="role"' in trends,'Trends editorial lane/role filters missing')
need("mode==='live'" in trends and "mode==='editorial'" in trends,'Trends dual-mode logic missing')
need('Live stats · snapshot público' in trends,'Trends live provenance text missing')

sitemap=read('sitemap.xml')
need('/trends/' in sitemap,'Sitemap missing /trends/')
need('/my-meta/' in sitemap,'Sitemap missing /my-meta/')
need('/roster/' in sitemap,'Sitemap missing /roster/')

live=Path('data/live-meta.json')
live_count=0
if live.exists():
    try:
        d=json.loads(live.read_text(encoding='utf-8'))
        heroes=d.get('heroes',[]);live_count=len(heroes)
        need(live_count>=100,f'live-meta has only {live_count} heroes')
        names=[h.get('name') for h in heroes if h.get('name')]
        need(len(names)==len(set(names)),'live-meta contains duplicate hero names')
        for h in heroes:
            wr=h.get('wr'); ban=h.get('ban'); pick=h.get('pick')
            need(isinstance(wr,(int,float)) and 30<=wr<=80,f'Invalid WR for {h.get("name")}')
            if ban is not None: need(isinstance(ban,(int,float)) and 0<=ban<=100,f'Invalid ban for {h.get("name")}')
            if pick is not None: need(isinstance(pick,(int,float)) and 0<=pick<=100,f'Invalid pick for {h.get("name")}')
    except Exception as e:
        errors.append(f'Cannot validate live-meta.json: {e}')

for path in ['scripts/enhance_home_ux.py','scripts/share_turn_draft.py']:
    src=read(path)
    need("'==='.slice((raw.length+3)%4)" not in src,f'Legacy Base64URL padding bug present in {path}')
    need("'='.repeat((4-raw.length%4)%4)" in src,f'Correct Base64URL padding missing in {path}')

search_src=read('scripts/inject_global_hero_search.py')
need("stats/heroes/" in search_src,'Global hero search source does not target statistical hero pages')
need("roster/${h.slug}" not in search_src,'Legacy wrong global-search roster route reintroduced')

hero_pages=list(Path('heroes').glob('*/index.html')) if Path('heroes').exists() else []
need(len(hero_pages)>=30,f'Only {len(hero_pages)} generated editorial hero pages found')
prov_pages=sum(1 for p in hero_pages if 'id="dataProvenance"' in p.read_text(encoding='utf-8'))
need(prov_pages==len(hero_pages),f'Data provenance present on only {prov_pages}/{len(hero_pages)} editorial hero pages')

stat_pages=list(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []
if live.exists():
    roster=read('roster/index.html')
    need(len(stat_pages)>=100,f'Only {len(stat_pages)} statistical hero pages generated')
    need(len(stat_pages)==live_count,f'Statistical pages ({len(stat_pages)}) do not match live hero count ({live_count})')
    need('id="dataProvenance"' in roster,'Live Roster provenance missing')
    need('id="globalHeroSearch"' in roster,'Live Roster global hero search missing')
    need('id="liveLeaders"' in roster,'Live Roster leaders missing')
    need('stats/heroes/' in roster,'Live Roster has no statistical hero routes')
    stat_prov=sum(1 for p in stat_pages if 'id="dataProvenance"' in p.read_text(encoding='utf-8'))
    need(stat_prov==len(stat_pages),f'Data provenance present on only {stat_prov}/{len(stat_pages)} statistical hero pages')

if errors:
    print('BUILD VALIDATION FAILED')
    for e in errors: print(f'- {e}')
    sys.exit(1)
print(f'Build validation passed: {len(hero_pages)} editorial pages, {len(stat_pages)} live-stat pages, dual Trends, leaders, global search and provenance present.')
