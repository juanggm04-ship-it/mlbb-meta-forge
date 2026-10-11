from pathlib import Path
import json,re,unicodedata,sys

SCORE=Path('data/meta-score.json');ROOT=Path('stats/heroes');errors=[]
def need(c,m):
    if not c: errors.append(m)
def slug(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')
rows=sorted(json.loads(SCORE.read_text(encoding='utf-8')).get('heroes',[]),key=lambda h:h.get('rank',9999)) if SCORE.exists() else []
need(len(rows)==133,f'Expected 133 Meta Score rows, found {len(rows)}')
by_slug={slug(r['name']):(i,r) for i,r in enumerate(rows)}
pages=sorted(ROOT.glob('*/index.html'))
need(len(pages)==133,f'Expected 133 stat pages, found {len(pages)}')
for p in pages:
    text=p.read_text(encoding='utf-8');pair=by_slug.get(p.parent.name)
    need(pair is not None,f'No score identity for {p}')
    if not pair: continue
    i,row=pair;expected=[]
    if i>0: expected.append(int(rows[i-1]['rank']))
    if i+1<len(rows): expected.append(int(rows[i+1]['rank']))
    need('id="heroScoreNeighbors"' in text,f'Neighbor section missing for {row["name"]}')
    need('La cercanía en Meta Score solo indica posición estadística próxima' in text,f'Neighbor disclaimer missing for {row["name"]}')
    ranks=[int(x) for x in re.findall(r'data-neighbor-rank="(\d+)"',text)]
    need(ranks==expected,f'Neighbor ranks mismatch for {row["name"]}: expected {expected}, got {ranks}')
    if expected:
        need('Comparar</a>' in text and 'Abrir ficha</a>' in text,f'Neighbor actions missing for {row["name"]}')
if errors:
    print('HERO SCORE NEIGHBOR VALIDATION FAILED')
    for e in errors[:50]: print('- '+e)
    if len(errors)>50: print(f'- ... and {len(errors)-50} more')
    sys.exit(1)
print('Hero score neighbor validation passed: all 133 pages point only to immediate Meta Score neighbors with statistical-only disclaimer.')
