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
    for key in ['lane','tier','role','note']:
        if not h.get(key): raise RuntimeError(f'Catalog missing {key} for {h["name"]}')

core=json.loads(CORE.read_text(encoding='utf-8'))
profile_names=set(core.get('profiles',{}))
if profile_names!=set(names):
    missing=sorted(set(names)-profile_names); extra=sorted(profile_names-set(names))
    raise RuntimeError(f'Catalog/editorial-core mismatch. missing_profiles={missing}, extra_profiles={extra}')

# Catalog is authoritative for homepage editorial metadata. Live rate stats remain untouched.
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

# Rebuild the legacy generator HEROES block from the shared catalog.
# Existing WR/ban values are preserved only as bundled fallbacks; apply_live_meta.py replaces them at build time.
src=GEN.read_text(encoding='utf-8')
gm=re.search(r'HEROES=\[(.*?)\]\n\nBY_NAME=',src,re.S)
if not gm: raise RuntimeError('Could not parse HEROES list in generate_heroes.py')
try:
    tuples=ast.literal_eval('['+gm.group(1)+']')
except Exception as e:
    raise RuntimeError(f'Could not parse HEROES tuples: {e}')
if len(tuples)!=34: raise RuntimeError(f'Generator fallback pool must contain 34 heroes, found {len(tuples)}')
fallback={t[0]:(t[3],t[4]) for t in tuples if len(t)>=7}
if set(fallback)!=set(names):
    raise RuntimeError(f'Catalog/generator fallback-name mismatch: catalog_only={sorted(set(names)-set(fallback))}, generator_only={sorted(set(fallback)-set(names))}')

lines=[]
for h in heroes:
    wr,ban=fallback[h['name']]
    lines.append(repr((h['name'],h['lane'],h['tier'],wr,ban,h['role'],h['note'])))
new_block='HEROES=[\n'+',\n'.join(lines)+']'
src=src[:gm.start()]+new_block+'\n\nBY_NAME='+src[gm.end():]
GEN.write_text(src,encoding='utf-8')

print('Editorial catalog synchronized: 34 heroes; catalog now authoritative for homepage and hero-generator editorial metadata')
