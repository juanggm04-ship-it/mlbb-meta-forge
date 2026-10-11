from pathlib import Path
import json,re,html,sys
from hero_identity import hero_key

LIVE=Path('data/live-meta.json')
SCORE=Path('data/meta-score.json')
CATALOG=Path('data/hero-catalog.json')
ROOT=Path('stats/heroes')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

for p in [LIVE,SCORE,CATALOG]: need(p.exists(),f'Missing hero-product dependency: {p}')
if errors:
    print('LIVE HERO PRODUCT VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)

live=json.loads(LIVE.read_text(encoding='utf-8'))
score=json.loads(SCORE.read_text(encoding='utf-8'))
catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
live_by={hero_key(h['name']):h for h in live.get('heroes',[]) if h.get('name')}
score_by={hero_key(h['name']):h for h in score.get('heroes',[]) if h.get('name')}
editorial={hero_key(h['name']) for h in catalog.get('heroes',[]) if h.get('name')}
pages=sorted(ROOT.glob('*/index.html'))
need(len(pages)==133,f'Expected 133 live hero pages, found {len(pages)}')
editorial_pages=0

for p in pages:
    text=p.read_text(encoding='utf-8')
    m=re.search(r'<h1>(.*?)</h1>',text,re.S)
    need(bool(m),f'Hero heading missing in {p}')
    if not m: continue
    name=html.unescape(re.sub(r'<.*?>','',m.group(1))).strip()
    key=hero_key(name)
    s=score_by.get(key)
    need(key in live_by,f'Live identity missing for {name}')
    need(s is not None,f'Meta Score missing for {name}')
    if not s: continue
    is_editorial=key in editorial
    if is_editorial: editorial_pages+=1

    need('id="productShellNav"' in text,f'Shared product navigation missing for {name}')
    need('href="../../../roster/" aria-current="page">Roster</a>' in text,f'Roster route not active in shell for {name}')
    need('id="heroProductSummary"' in text,f'Hero product summary missing for {name}')
    need(f'data-meta-score="{float(s["score"]):.1f}"' in text,f'Meta Score summary mismatch for {name}')
    need(f'data-meta-rank="{int(s["rank"])}"' in text,f'Meta rank summary mismatch for {name}')
    need(f'data-editorial="{"true" if is_editorial else "false"}"' in text,f'Editorial coverage flag mismatch for {name}')
    need('META SCORE · NO TIER' in text,f'Meta Score distinction missing for {name}')
    need('id="heroQuickActions"' in text,f'Quick actions missing for {name}')
    need('id="heroQuickWatch"' in text and 'id="liveWatchToggle"' in text,f'Watchlist proxy/source missing for {name}')
    need('MutationObserver(sync).observe(source' in text,f'Watchlist proxy sync missing for {name}')
    for token in ['../../../roster/','../../../compare/?a=','../../../trends/','../../../my-meta/','../../../methodology.html']:
        need(token in text,f'Hero product route {token} missing for {name}')
    need('id="heroSourceDetails"' in text,f'Collapsed provenance missing for {name}')
    need('id="heroMetaScore"' in text,f'Meta Score detail section missing for {name}')
    need('id="dataProvenance"' in text,f'Global data provenance missing for {name}')
    editorial_cta=f'../../../heroes/{p.parent.name}/'
    if is_editorial:
        need('Análisis editorial</a>' in text and editorial_cta in text,f'Editorial CTA missing for curated hero {name}')
    else:
        need('Análisis editorial</a>' not in text,f'Invented editorial CTA on stats-only hero {name}')

need(editorial_pages==34,f'Expected 34 editorial-capable live hero pages, found {editorial_pages}')
if errors:
    print('LIVE HERO PRODUCT VALIDATION FAILED')
    for e in errors[:60]: print('- '+e)
    if len(errors)>60: print(f'- ... and {len(errors)-60} more')
    sys.exit(1)
print(f'Live hero product validation passed: {len(pages)} pages, {editorial_pages} editorial-capable and {len(pages)-editorial_pages} stats-only, with shared navigation, score hierarchy, Watchlist, Compare, Trends and collapsed provenance.')
