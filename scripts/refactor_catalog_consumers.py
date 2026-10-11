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
import json

ROOT=Path('.')
INDEX=ROOT/'index.html'
CAT=ROOT/'data'/'hero-catalog.json'
OUT=ROOT/'trends'/'index.html'
if not INDEX.exists(): raise RuntimeError('index.html not found')
if not CAT.exists(): raise RuntimeError('data/hero-catalog.json not found')
catalog=json.loads(CAT.read_text(encoding='utf-8'))
editorial=[{'name':h.get('name'),'lane':h.get('lane'),'role':h.get('role'),'tier':h.get('tier')} for h in catalog.get('heroes',[]) if h.get('name')]
if len(editorial)!=34: raise RuntimeError(f'Editorial catalog must contain 34 heroes, found {len(editorial)}')
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
import json

ROOT=Path('.')
out=ROOT/'my-meta';out.mkdir(exist_ok=True)
index=ROOT/'index.html'
CAT=ROOT/'data'/'hero-catalog.json'
if not CAT.exists(): raise RuntimeError('data/hero-catalog.json not found')
catalog=json.loads(CAT.read_text(encoding='utf-8'))
heroes=catalog.get('heroes',[])
if len(heroes)!=34: raise RuntimeError(f'Editorial catalog must contain 34 heroes, found {len(heroes)}')
editorial={h['name']:{'lane':h.get('lane'),'role':h.get('role'),'tier':h.get('tier')} for h in heroes if h.get('name')}
if len(editorial)!=34: raise RuntimeError(f'Editorial catalog names must be unique and complete, found {len(editorial)}')
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
    if "re.search(r'const DATA=" in text:
        raise RuntimeError(f'{p} still parses homepage DATA for editorial metadata')

print('Refactored Trends and My Meta to consume data/hero-catalog.json directly')
