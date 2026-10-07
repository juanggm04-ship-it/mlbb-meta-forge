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
    'dataHealth','metaChanges','watchlistPanel','watchlistPulse','dataProvenance'
]
for item in required_ids:
    need(f'id="{item}"' in html,f'Missing homepage module: #{item}')

need('LIVE STATS' in html and 'EDITORIAL' in html,'Homepage provenance labels missing')
need('trends/' in html,'Homepage has no link/reference to Trends')
need('my-meta/' in html,'Homepage has no link/reference to My Meta')

trends=read('trends/index.html')
my_meta=read('my-meta/index.html')
need('<title>' in trends and 'Trend' in trends,'Trends page title missing')
need('<title>' in my_meta and ('Meta' in my_meta or 'meta' in my_meta),'My Meta page title missing')
need('id="dataProvenance"' in trends,'Trends provenance missing')
need('id="dataProvenance"' in my_meta,'My Meta provenance missing')

sitemap=read('sitemap.xml')
need('/trends/' in sitemap,'Sitemap missing /trends/')
need('/my-meta/' in sitemap,'Sitemap missing /my-meta/')

live=Path('data/live-meta.json')
if live.exists():
    try:
        d=json.loads(live.read_text(encoding='utf-8'))
        heroes=d.get('heroes',[])
        need(len(heroes)>=100,f'live-meta has only {len(heroes)} heroes')
        names=[h.get('name') for h in heroes if h.get('name')]
        need(len(names)==len(set(names)),'live-meta contains duplicate hero names')
        for h in heroes:
            wr=h.get('wr'); ban=h.get('ban'); pick=h.get('pick')
            need(isinstance(wr,(int,float)) and 30<=wr<=80,f'Invalid WR for {h.get("name")}')
            if ban is not None: need(isinstance(ban,(int,float)) and 0<=ban<=100,f'Invalid ban for {h.get("name")}')
            if pick is not None: need(isinstance(pick,(int,float)) and 0<=pick<=100,f'Invalid pick for {h.get("name")}')
    except Exception as e:
        errors.append(f'Cannot validate live-meta.json: {e}')

# Catch the historical Base64URL padding bug if it is reintroduced.
for path in ['scripts/enhance_home_ux.py','scripts/share_turn_draft.py']:
    src=read(path)
    need("'==='.slice((raw.length+3)%4)" not in src,f'Legacy Base64URL padding bug present in {path}')
    need("'='.repeat((4-raw.length%4)%4)" in src,f'Correct Base64URL padding missing in {path}')

# Generated hero pages should exist and have at least the original public pool size.
hero_pages=list(Path('heroes').glob('*/index.html')) if Path('heroes').exists() else []
need(len(hero_pages)>=30,f'Only {len(hero_pages)} generated hero pages found')
prov_pages=sum(1 for p in hero_pages if 'id="dataProvenance"' in p.read_text(encoding='utf-8'))
need(prov_pages==len(hero_pages),f'Data provenance present on only {prov_pages}/{len(hero_pages)} hero pages')

if errors:
    print('BUILD VALIDATION FAILED')
    for e in errors: print(f'- {e}')
    sys.exit(1)
print(f'Build validation passed: {len(hero_pages)} hero pages, core modules and provenance present.')
