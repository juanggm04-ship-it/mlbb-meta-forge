from pathlib import Path

TRENDS=Path('scripts/generate_dual_trends.py')
MY_META=Path('scripts/generate_my_meta.py')

for p in [TRENDS,MY_META]:
    if not p.exists():
        raise RuntimeError(f'Missing catalog consumer: {p}')

trends=TRENDS.read_text(encoding='utf-8')
old_trends="""from pathlib import Path
import json,re

ROOT=Path('.')
INDEX=ROOT/'index.html'
OUT=ROOT/'trends'/'index.html'
if not INDEX.exists(): raise RuntimeError('index.html not found')
src=INDEX.read_text(encoding='utf-8')
m=re.search(r'const DATA=(\\{.*?\\});\\nconst DRAFTS=',src,re.S)
if not m: raise RuntimeError('Could not locate DATA object in index.html')
data=json.loads(m.group(1))
editorial=[{'name':h.get('name'),'lane':h.get('lane'),'role':h.get('role'),'tier':h.get('tier')} for h in data.get('heroes',[]) if h.get('name')]
if len(editorial)<30: raise RuntimeError(f'Editorial pool too small: {len(editorial)}')
EDITORIAL=json.dumps(editorial,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')
"""
new_trends="""from pathlib import Path
import json,re,unicodedata

ROOT=Path('.')
INDEX=ROOT/'index.html'
CAT=ROOT/'data'/'hero-catalog.json'
LIVE=ROOT/'data'/'live-meta.json'
OUT=ROOT/'trends'/'index.html'
if not INDEX.exists(): raise RuntimeError('index.html not found')
if not CAT.exists(): raise RuntimeError('data/hero-catalog.json not found')
if not LIVE.exists(): raise RuntimeError('data/live-meta.json not found')
def _norm(s):
    s=str(s or '').lower().replace('&','and')
    s=''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','',s)
catalog=json.loads(CAT.read_text(encoding='utf-8'))
live=json.loads(LIVE.read_text(encoding='utf-8'))
live_names={_norm(h.get('name')):h.get('name') for h in live.get('heroes',[]) if h.get('name')}
editorial=[]
matched=0
for h in catalog.get('heroes',[]):
    if not h.get('name'): continue
    live_name=live_names.get(_norm(h.get('name')))
    if live_name: matched+=1
    editorial.append({'name':live_name or h.get('name'),'canonical_name':h.get('name'),'lane':h.get('lane'),'role':h.get('role'),'tier':h.get('tier')})
if len(editorial)!=34: raise RuntimeError(f'Editorial catalog must contain 34 heroes, found {len(editorial)}')
if matched!=34: raise RuntimeError(f'Only {matched}/34 editorial heroes matched the live roster by normalized name')
EDITORIAL=json.dumps(editorial,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')
"""
if "CAT=ROOT/'data'/'hero-catalog.json'" not in trends:
    if old_trends not in trends:
        raise RuntimeError('Trends legacy editorial extraction block not found')
    trends=trends.replace(old_trends,new_trends,1)
    TRENDS.write_text(trends,encoding='utf-8')

my_meta=MY_META.read_text(encoding='utf-8')
old_my_meta="""from pathlib import Path
import json,re

ROOT=Path('.')
out=ROOT/'my-meta';out.mkdir(exist_ok=True)
index=ROOT/'index.html'
editorial={}
if index.exists():
    src=index.read_text(encoding='utf-8')
    m=re.search(r'const DATA=(\\{.*?\\});\\nconst DRAFTS=',src,re.S)
    if m:
        try:
            d=json.loads(m.group(1))
            for h in d.get('heroes',[]):
                if h.get('name'):
                    editorial[h['name']]={'lane':h.get('lane'),'role':h.get('role'),'tier':h.get('tier')}
        except Exception:
            pass
EDITORIAL=json.dumps(editorial,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')
"""
new_my_meta="""from pathlib import Path
import json,re,unicodedata

ROOT=Path('.')
out=ROOT/'my-meta';out.mkdir(exist_ok=True)
index=ROOT/'index.html'
CAT=ROOT/'data'/'hero-catalog.json'
LIVE=ROOT/'data'/'live-meta.json'
if not CAT.exists(): raise RuntimeError('data/hero-catalog.json not found')
if not LIVE.exists(): raise RuntimeError('data/live-meta.json not found')
def _norm(s):
    s=str(s or '').lower().replace('&','and')
    s=''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','',s)
catalog=json.loads(CAT.read_text(encoding='utf-8'))
live=json.loads(LIVE.read_text(encoding='utf-8'))
heroes=catalog.get('heroes',[])
if len(heroes)!=34: raise RuntimeError(f'Editorial catalog must contain 34 heroes, found {len(heroes)}')
live_names={_norm(h.get('name')):h.get('name') for h in live.get('heroes',[]) if h.get('name')}
editorial={}
matched=0
for h in heroes:
    if not h.get('name'): continue
    live_name=live_names.get(_norm(h.get('name')))
    if live_name: matched+=1
    key=live_name or h.get('name')
    editorial[key]={'lane':h.get('lane'),'role':h.get('role'),'tier':h.get('tier'),'canonical_name':h.get('name')}
if len(editorial)!=34: raise RuntimeError(f'Editorial catalog names must be unique and complete, found {len(editorial)}')
if matched!=34: raise RuntimeError(f'Only {matched}/34 editorial heroes matched the live roster by normalized name')
EDITORIAL=json.dumps(editorial,ensure_ascii=False,separators=(',',':')).replace('</','<\\\\/')
"""
if "CAT=ROOT/'data'/'hero-catalog.json'" not in my_meta:
    if old_my_meta not in my_meta:
        raise RuntimeError('My Meta legacy editorial extraction block not found')
    my_meta=my_meta.replace(old_my_meta,new_my_meta,1)
    MY_META.write_text(my_meta,encoding='utf-8')

for p in [TRENDS,MY_META]:
    text=p.read_text(encoding='utf-8')
    if "CAT=ROOT/'data'/'hero-catalog.json'" not in text:
        raise RuntimeError(f'{p} did not switch to shared catalog')
    if "LIVE=ROOT/'data'/'live-meta.json'" not in text:
        raise RuntimeError(f'{p} does not resolve catalog aliases against live roster')
    if "re.search(r'const DATA=" in text:
        raise RuntimeError(f'{p} still parses homepage DATA for editorial metadata')

print('Refactored Trends and My Meta to consume hero catalog directly with normalized live-name resolution')
