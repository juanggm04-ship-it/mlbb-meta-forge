from pathlib import Path
import ast,json,re

CAT=Path('data/hero-catalog.json')
CORE=Path('data/editorial-core.json')
INDEX=Path('index.html')
GEN=Path('scripts/generate_heroes.py')

for p in [CAT,CORE,INDEX,GEN]:
    if not p.exists(): raise RuntimeError(f'Missing required file: {p}')

catalog=json.loads(CAT.read_text(encoding='utf-8'))
heroes=catalog.get('heroes',[])
if len(heroes)!=34: raise RuntimeError(f'Editorial catalog must contain 34 heroes, found {len(heroes)}')
names=[h.get('name') for h in heroes]
if any(not n for n in names) or len(set(names))!=34: raise RuntimeError('Editorial catalog has missing or duplicate names')
by={h['name']:h for h in heroes}
for h in heroes:
    for key in ['lane','tier','role']:
        if not h.get(key): raise RuntimeError(f'Catalog missing {key} for {h["name"]}')

core=json.loads(CORE.read_text(encoding='utf-8'))
profile_names=set(core.get('profiles',{}))
if profile_names!=set(names):
    missing=sorted(set(names)-profile_names); extra=sorted(profile_names-set(names))
    raise RuntimeError(f'Catalog/editorial-core mismatch. missing_profiles={missing}, extra_profiles={extra}')

# Keep homepage editorial metadata aligned to the catalog. Live rate stats remain untouched.
html=INDEX.read_text(encoding='utf-8')
m=re.search(r'const DATA=(\{.*?\});\nconst DRAFTS=',html,re.S)
if not m: raise RuntimeError('Could not locate DATA object in index.html')
data=json.loads(m.group(1))
matched=0
for h in data.get('heroes',[]):
    c=by.get(h.get('name'))
    if not c: continue
    h['lane']=c['lane']; h['role']=c['role']; h['tier']=c['tier']; matched+=1
if matched!=34: raise RuntimeError(f'Homepage/catalog match expected 34 heroes, found {matched}')
packed=json.dumps(data,ensure_ascii=False,separators=(',',':'))
INDEX.write_text(html[:m.start(1)]+packed+html[m.end(1):],encoding='utf-8')

# Guard the legacy hero generator until it is fully refactored to consume the catalog directly.
src=GEN.read_text(encoding='utf-8')
gm=re.search(r'HEROES=\[(.*?)\]\n\nBY_NAME=',src,re.S)
if not gm: raise RuntimeError('Could not parse legacy HEROES list in generate_heroes.py')
try:
    tuples=ast.literal_eval('['+gm.group(1)+']')
except Exception as e:
    raise RuntimeError(f'Could not parse legacy HEROES tuples: {e}')
if len(tuples)!=34: raise RuntimeError(f'Legacy generator must contain 34 heroes, found {len(tuples)}')
gen_names={t[0] for t in tuples}
if gen_names!=set(names):
    raise RuntimeError(f'Catalog/generator hero-name mismatch: catalog_only={sorted(set(names)-gen_names)}, generator_only={sorted(gen_names-set(names))}')
for t in tuples:
    name,lane,tier,_,_,role,note=t
    c=by[name]
    if (lane,tier,role)!=(c['lane'],c['tier'],c['role']):
        raise RuntimeError(f'Catalog/generator editorial metadata mismatch for {name}: generator={(lane,tier,role)}, catalog={(c["lane"],c["tier"],c["role"])}')

print('Editorial catalog synchronized: 34 heroes; homepage metadata aligned; generator and editorial core consistent')
