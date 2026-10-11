from pathlib import Path
import json,re,sys

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

cat_path=Path('data/hero-catalog.json')
core_path=Path('data/editorial-core.json')
index_path=Path('index.html')
need(cat_path.exists(),'Editorial catalog missing')
need(core_path.exists(),'Editorial core missing')
need(index_path.exists(),'Homepage missing')

if cat_path.exists() and core_path.exists():
    cat=json.loads(cat_path.read_text(encoding='utf-8'))
    heroes=cat.get('heroes',[])
    names=[h.get('name') for h in heroes if h.get('name')]
    need(cat.get('scope')=='editorial','Catalog scope must be editorial')
    need(len(heroes)==34,f'Catalog must contain 34 heroes, found {len(heroes)}')
    need(len(names)==len(set(names)),'Catalog contains duplicate hero names')
    for h in heroes:
        for key in ['name','lane','tier','role']:
            need(bool(h.get(key)),f'Catalog missing {key} for {h.get("name")}')
    core=json.loads(core_path.read_text(encoding='utf-8'))
    profiles=set(core.get('profiles',{}))
    need(set(names)==profiles,f'Catalog/profile names differ: catalog_only={sorted(set(names)-profiles)}, profile_only={sorted(profiles-set(names))}')

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

hero_pages=list(Path('heroes').glob('*/index.html')) if Path('heroes').exists() else []
need(len(hero_pages)==34,f'Expected 34 generated editorial hero pages, found {len(hero_pages)}')

if errors:
    print('EDITORIAL CATALOG VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Editorial catalog validation passed: 34 heroes aligned across catalog, homepage, editorial core and generated pages.')
