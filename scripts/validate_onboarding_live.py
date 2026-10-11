from pathlib import Path
import json,re,sys

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

index=Path('index.html')
live=Path('data/live-meta.json')
cat=Path('data/hero-catalog.json')
need(index.exists(),'Homepage missing')
need(live.exists(),'Live meta missing')
need(cat.exists(),'Editorial catalog missing')

expected_live=0
expected_editorial=0
if live.exists():
    data=json.loads(live.read_text(encoding='utf-8'))
    names=[h.get('name') for h in data.get('heroes',[]) if h.get('name')]
    expected_live=len(names)
    need(expected_live>=100,f'Live roster too small for onboarding: {expected_live}')
    need(len(names)==len(set(names)),'Live roster contains duplicate hero names')
if cat.exists():
    editorial=json.loads(cat.read_text(encoding='utf-8')).get('heroes',[])
    expected_editorial=len(editorial)
    need(expected_editorial==34,f'Editorial catalog expected 34 heroes, found {expected_editorial}')

if index.exists():
    text=index.read_text(encoding='utf-8')
    need('window.MF_ONBOARD_HEROES=' in text,'Live onboarding hero pool missing')
    need('window.MF_ONBOARD_HEROES||window.DATA?.heroes' in text,'Onboarding does not prefer full live pool')
    need('data-onboarding-live=' in text,'Onboarding live-count marker missing')
    need('favoritos del roster live' in text,'Onboarding copy does not describe live roster selection')
    m=re.search(r'window\.MF_ONBOARD_HEROES=(\[.*?\]);</script>',text,re.S)
    need(bool(m),'Could not parse embedded onboarding live pool')
    if m:
        pool=json.loads(m.group(1))
        need(len(pool)==expected_live,f'Embedded onboarding pool has {len(pool)} heroes; live roster has {expected_live}')
        names=[h.get('name') for h in pool if h.get('name')]
        need(len(names)==len(set(names)),'Embedded onboarding pool contains duplicate names')
        curated=[h for h in pool if h.get('editorial')]
        need(len(curated)==expected_editorial,f'Embedded onboarding pool marks {len(curated)} editorial heroes; expected {expected_editorial}')
        need(all(h.get('lane') for h in curated),'At least one editorial onboarding hero is missing lane metadata')
        stats_only=[h for h in pool if not h.get('editorial')]
        need(all(not h.get('lane') for h in stats_only),'Stats-only onboarding heroes should not receive invented lane metadata')

if errors:
    print('LIVE ONBOARDING VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Live onboarding validation passed: {expected_live} selectable heroes, {expected_editorial} with editorial lane metadata, stats-only heroes remain unclassified.')
