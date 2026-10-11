from pathlib import Path
import json,sys
from hero_identity import hero_key,index_by_hero_key,semantic_rate_rows

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

LIVE=Path('data/live-meta.json')
CAT=Path('data/hero-catalog.json')
HISTORY=Path('data/meta-history.json')
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

    # Parser v2 is the first explicit rate-unit contract. During the one-time
    # migration an older checked-in snapshot may still have no parser_version;
    # once v2 appears, enforce it strictly everywhere.
    if live.get('parser_version') is not None:
        need(live.get('parser_version')==2,f'Expected parser_version=2, found {live.get("parser_version")}')
        need(live.get('rate_unit')=='percentage_points',f'Expected percentage_points rate unit, found {live.get("rate_unit")}')
        picks=[h.get('pick') for h in live.get('heroes',[]) if isinstance(h.get('pick'),(int,float))]
        need(len(picks)==len(live_map),f'Expected pick rate for every live hero, found {len(picks)}/{len(live_map)}')
        need(bool(picks) and max(picks)<=20,f'Pick-rate scale looks wrong; maximum={max(picks) if picks else None}')
        if HISTORY.exists():
            hist=json.loads(HISTORY.read_text(encoding='utf-8'))
            need(hist.get('parser_version')==2,'History parser_version is not 2 after rate-unit migration')
            need(hist.get('rate_unit')=='percentage_points','History rate unit is not percentage_points')
            need(len(hist.get('snapshots',[]))>=1,'History has no snapshots after parser migration')

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
    need("RATE_UNIT='percentage_points'" in text,'Sync does not declare percentage-point rate units')
    need('PARSER_VERSION=2' in text,'Sync parser version is not pinned to v2')
    start=text.find('def semantic_view')
    end=text.find('\ndef ',start+4)
    block=text[start:end] if start!=-1 and end!=-1 else ''
    need(bool(block),'Could not isolate semantic_view() for validation')
    need("'tier'" not in block and 'source_updated' not in block and 'fetched_at' not in block,'Semantic history change detection still depends on non-game metadata')

if errors:
    print('HERO IDENTITY VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Hero identity validation passed: shared aliases, stable semantic history, parser v2 percentage-point contract.')
