from pathlib import Path
import json,sys
from hero_identity import hero_key,index_by_hero_key,semantic_rate_rows

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

LIVE=Path('data/live-meta.json')
CAT=Path('data/hero-catalog.json')
need(LIVE.exists(),'live-meta.json missing')
need(CAT.exists(),'hero-catalog.json missing')

if LIVE.exists() and CAT.exists():
    live=json.loads(LIVE.read_text(encoding='utf-8'))
    cat=json.loads(CAT.read_text(encoding='utf-8'))
    try:
        live_map=index_by_hero_key(live.get('heroes',[]))
        cat_map=index_by_hero_key(cat.get('heroes',[]))
    except Exception as e:
        errors.append(str(e))
        live_map={};cat_map={}
    need(len(live_map)>=100,f'Expected 100+ unique live hero identities, found {len(live_map)}')
    need(len(cat_map)==34,f'Expected 34 unique editorial identities, found {len(cat_map)}')
    matched=set(cat_map)&set(live_map)
    need(len(matched)==34,f'Expected 34/34 editorial heroes to resolve in live roster, found {len(matched)}')
    sem=semantic_rate_rows(live.get('heroes',[]))
    need(len(sem)==len(live_map),'Semantic rate rows do not preserve unique live identity count')

need(hero_key('Popol & Kupa')==hero_key('Popol and Kupa'),'Ampersand/and alias normalization regressed')
need(hero_key('Yi Sun-shin')==hero_key('Yi Sun shin'),'Punctuation normalization regressed')

for path in ['scripts/apply_live_meta.py','scripts/enhance_onboarding_live_pool.py','scripts/refactor_catalog_consumers.py']:
    p=Path(path); need(p.exists(),f'Missing identity consumer: {path}')
    if p.exists():
        text=p.read_text(encoding='utf-8')
        need('hero_identity' in text,f'{path} does not use shared hero identity')

sync=Path('scripts/sync_public_meta.py')
need(sync.exists(),'sync_public_meta.py missing')
if sync.exists():
    text=sync.read_text(encoding='utf-8')
    need('semantic_rate_rows' in text,'Sync does not use canonical semantic rate rows')
    start=text.find('def semantic_view')
    end=text.find('def append_history',start)
    block=text[start:end] if start!=-1 and end!=-1 else ''
    need("'tier'" not in block and 'source_updated' not in block,'Semantic history change detection still depends on tier/source timestamp')

if errors:
    print('HERO IDENTITY VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Hero identity validation passed: shared normalization, live/editorial matching and stable stat-only semantic history contract.')
