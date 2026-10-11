from pathlib import Path
import json,re,sys
from hero_identity import hero_key,index_by_hero_key

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

cat_path=Path('data/hero-catalog.json')
core_path=Path('data/editorial-core.json')
live_path=Path('data/live-meta.json')
index_path=Path('index.html')
need(cat_path.exists(),'Editorial catalog missing')
need(core_path.exists(),'Editorial core missing')
need(live_path.exists(),'Live meta missing')
need(index_path.exists(),'Homepage missing')

if cat_path.exists() and core_path.exists():
    cat=json.loads(cat_path.read_text(encoding='utf-8'))
    heroes=cat.get('heroes',[])
    names=[h.get('name') for h in heroes if h.get('name')]
    need(cat.get('scope')=='editorial','Catalog scope must be editorial')
    need(len(heroes)==34,f'Catalog must contain 34 heroes, found {len(heroes)}')
    need(len(names)==len(set(names)),'Catalog contains duplicate hero names')
    try:
        catalog_index=index_by_hero_key(heroes)
    except Exception as e:
        errors.append(str(e)); catalog_index={}
    need(len(catalog_index)==34,f'Catalog must contain 34 unique shared hero identities, found {len(catalog_index)}')
    for h in heroes:
        for key in ['name','lane','tier','role']:
            need(bool(h.get(key)),f'Catalog missing {key} for {h.get("name")}')
    core=json.loads(core_path.read_text(encoding='utf-8'))
    profiles=set(core.get('profiles',{}))
    need(set(names)==profiles,f'Catalog/profile names differ: catalog_only={sorted(set(names)-profiles)}, profile_only={sorted(profiles-set(names))}')

    if live_path.exists():
        live=json.loads(live_path.read_text(encoding='utf-8'))
        try:
            live_index=index_by_hero_key(live.get('heroes',[]))
        except Exception as e:
            errors.append(str(e)); live_index={}
        missing=sorted(h['name'] for h in heroes if hero_key(h.get('name')) not in live_index)
        matched=set(catalog_index)&set(live_index)
        need(len(matched)==34,f'Only {len(matched)}/34 catalog heroes resolve against live roster through shared identity; missing={missing}')

    if index_path.exists():
        src=index_path.read_text(encoding='utf-8')
        m=re.search(r'const DATA=(\{.*?\});\nconst DRAFTS=',src,re.S)
        need(bool(m),'Homepage DATA object not found for catalog validation')
        if m:
            data=json.loads(m.group(1))
            page={h.get('name'):h for h in data.get('heroes',[]) if h.get('name')}
            need(set(names)==set(page),'Homepage editorial hero names differ from catalog')
            for c in heroes:
                h=page.get(c['name'],{})
                need(h.get('lane')==c['lane'],f'Homepage lane differs from catalog for {c["name"]}')
                need(h.get('role')==c['role'],f'Homepage role differs from catalog for {c["name"]}')
                need(h.get('tier')==c['tier'],f'Homepage tier differs from catalog for {c["name"]}')

for consumer in [Path('scripts/generate_dual_trends.py'),Path('scripts/generate_my_meta.py')]:
    need(consumer.exists(),f'Catalog consumer missing: {consumer}')
    if consumer.exists():
        text=consumer.read_text(encoding='utf-8')
        need("CAT=ROOT/'data'/'hero-catalog.json'" in text,f'{consumer} does not read shared hero catalog directly')
        need("LIVE=ROOT/'data'/'live-meta.json'" in text,f'{consumer} does not resolve catalog names against live roster')
        need('from hero_identity import hero_key, index_by_hero_key' in text,f'{consumer} does not use the shared alias resolver')
        need('matched!=34' in text,f'{consumer} does not require all 34 editorial heroes to resolve live aliases')
        need("re.search(r'const DATA=" not in text,f'{consumer} still parses homepage DATA for editorial metadata')
        need("catalog.get('heroes',[])" in text,f'{consumer} does not consume catalog heroes')

hero_pages=list(Path('heroes').glob('*/index.html')) if Path('heroes').exists() else []
need(len(hero_pages)==34,f'Expected 34 generated editorial hero pages, found {len(hero_pages)}')

trends=Path('trends/index.html')
my_meta=Path('my-meta/index.html')
need(trends.exists(),'Generated Trends page missing')
need(my_meta.exists(),'Generated My Meta page missing')
if trends.exists():
    text=trends.read_text(encoding='utf-8')
    need('EDITORIAL<small>34 héroes' in text,'Trends editorial mode no longer reports 34 curated heroes')
if my_meta.exists():
    text=my_meta.read_text(encoding='utf-8')
    need('EDITORIAL ROLE RADAR' in text,'My Meta editorial role radar missing')

if errors:
    print('EDITORIAL CATALOG VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Editorial catalog validation passed: 34 heroes align across catalog/core/homepage and resolve live aliases through the shared identity module.')
