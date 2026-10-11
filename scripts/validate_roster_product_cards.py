from pathlib import Path
import json, re, sys
from hero_identity import hero_key

ROSTER=Path('roster/index.html')
SCORE=Path('data/meta-score.json')
CATALOG=Path('data/hero-catalog.json')
errors=[]

def need(cond,msg):
    if not cond: errors.append(msg)

for p in [ROSTER,SCORE,CATALOG]:
    need(p.exists(),f'Missing Roster product-card validation dependency: {p}')
if errors:
    print('ROSTER PRODUCT CARD VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)

text=ROSTER.read_text(encoding='utf-8')
score=json.loads(SCORE.read_text(encoding='utf-8'))
catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
score_rows=score.get('heroes',[])
editorial_rows=catalog.get('heroes',[])
need(len(score_rows)==133,f'Expected 133 score rows, got {len(score_rows)}')
need(len(editorial_rows)==34,f'Expected 34 editorial rows, got {len(editorial_rows)}')

for token,msg in [
    ('id="roster-product-cards-style"','Roster product-card CSS missing'),
    ('id="roster-product-cards-script"','Roster product-card runtime missing'),
    ('id="rosterSortNote"','Roster Meta Score sort note missing'),
    ('<option value="score">Mayor Meta Score</option>','Meta Score sort option missing'),
    ("sort.value='score'",'Meta Score is not the default sort'),
    ("const WATCH_KEY='mf_watchlist_v1'",'Roster cards do not use shared Watchlist storage'),
    ('data-roster-watch','Roster quick Watchlist control missing'),
    ('../compare/?a=${encodeURIComponent(h.name)}','Roster quick Compare route missing'),
    ('article class="card roster-card"','Roster cards are not interactive article cards'),
    ('roster-card-score','Roster Meta Score card block missing'),
    ('data-meta-rank','Stable Meta Score rank marker missing'),
    ('El #rank mostrado en cada tarjeta siempre corresponde a Meta Score','Stable-rank explanation missing'),
]:
    need(token in text,msg)
need('#${i+1}' not in text,'Legacy filtered-position rank is still present in Roster runtime')
need('<a class="card" href="../stats/heroes/' not in text,'Legacy whole-card anchor runtime is still present')

m=re.search(r'id="roster-product-cards-script">const HEROES=(\[.*?\]);const grid=',text,re.S)
need(bool(m),'Could not parse enhanced Roster HEROES payload')
rows=[]
if m:
    try: rows=json.loads(m.group(1))
    except Exception as exc: errors.append(f'Enhanced Roster HEROES payload is invalid JSON: {exc}')
need(len(rows)==133,f'Enhanced Roster payload should contain 133 heroes, got {len(rows)}')

score_by={hero_key(r['name']):r for r in score_rows if r.get('name')}
editorial={hero_key(r['name']) for r in editorial_rows if r.get('name')}
seen=set()
editorial_count=0
for r in rows:
    name=r.get('name')
    key=hero_key(name)
    need(bool(name),f'Roster row without name: {r}')
    need(key not in seen,f'Duplicate Roster hero identity: {name}')
    seen.add(key)
    expected=score_by.get(key)
    need(expected is not None,f'Roster row has no Meta Score source: {name}')
    if expected:
        need(r.get('score')==expected.get('score'),f'Meta Score mismatch for {name}: roster={r.get("score")} source={expected.get("score")}')
        need(r.get('rank')==expected.get('rank'),f'Meta rank mismatch for {name}: roster={r.get("rank")} source={expected.get("rank")}')
    should_editorial=key in editorial
    need(bool(r.get('editorial'))==should_editorial,f'Editorial badge mismatch for {name}')
    if r.get('editorial'): editorial_count+=1
need(editorial_count==34,f'Expected 34 editorial Roster cards, got {editorial_count}')
need(len(seen)==133,f'Expected 133 unique hero identities in Roster payload, got {len(seen)}')

# Score sort must be monotonic when recomputed from the embedded payload.
ordered=sorted(rows,key=lambda r:(-float(r.get('score',-1)),r.get('name','')))
source_order=sorted(score_rows,key=lambda r:(int(r.get('rank',9999)),r.get('name','')))
need([hero_key(r['name']) for r in ordered]==[hero_key(r['name']) for r in source_order], 'Embedded Meta Score ordering does not reproduce canonical ranks')

if errors:
    print('ROSTER PRODUCT CARD VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Roster product-card validation passed: heroes={len(rows)}; editorial={editorial_count}; default_sort=Meta Score; quick Compare + Watchlist use shared state.')
