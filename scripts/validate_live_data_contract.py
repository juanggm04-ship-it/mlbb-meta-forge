from pathlib import Path
import json,datetime,sys
from hero_identity import hero_key,index_by_hero_key

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

def parse_iso(value,label):
    try:
        return datetime.datetime.fromisoformat(str(value).replace('Z','+00:00'))
    except Exception:
        errors.append(f'{label} is not a valid ISO timestamp: {value!r}')
        return None

live_path=Path('data/live-meta.json')
history_path=Path('data/meta-history.json')
need(live_path.exists(),'live-meta.json missing')
need(history_path.exists(),'meta-history.json missing')

live={}
if live_path.exists():
    try: live=json.loads(live_path.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'Cannot parse live-meta.json: {e}')

if live:
    need(live.get('identity_version')==1,f'identity_version must be 1, found {live.get("identity_version")}')
    need(live.get('parser_version')==2,f'parser_version must be 2, found {live.get("parser_version")}')
    need(live.get('rate_unit')=='percentage_points',f'rate_unit must be percentage_points, found {live.get("rate_unit")}')
    need(live.get('freshness_basis')=='source',f'freshness_basis must be source now that measuredAt is available, found {live.get("freshness_basis")}')
    measured=parse_iso(live.get('source_updated'),'source_updated')
    fetched=parse_iso(live.get('fetched_at'),'fetched_at')
    if measured and fetched:
        need(measured<=fetched,'source_updated cannot be later than fetched_at')
        need(live.get('updated')==measured.date().isoformat(),f'updated must equal source measurement date {measured.date().isoformat()}')
    heroes=live.get('heroes',[])
    need(len(heroes)==133,f'Expected 133 ranked live heroes, found {len(heroes)}')
    need(live.get('total')==len(heroes),f'live total field {live.get("total")} does not match hero rows {len(heroes)}')
    try:
        idx=index_by_hero_key(heroes)
        need(len(idx)==len(heroes),'Normalized live hero identity count differs from row count')
    except Exception as e:
        errors.append(str(e))
    picks=[]; bans=[]
    for h in heroes:
        name=h.get('name')
        need(h.get('key')==hero_key(name),f'Hero key mismatch for {name}')
        wr=h.get('wr');ban=h.get('ban');pick=h.get('pick')
        need(isinstance(wr,(int,float)) and 30<=wr<=80,f'Invalid WR for {name}: {wr}')
        need(isinstance(ban,(int,float)) and 0<=ban<=100,f'Invalid ban rate for {name}: {ban}')
        need(isinstance(pick,(int,float)) and 0<=pick<=20,f'Invalid pick-rate scale for {name}: {pick}')
        if isinstance(ban,(int,float)): bans.append(ban)
        if isinstance(pick,(int,float)): picks.append(pick)
    if picks:
        need(max(picks)<=20,f'Pick-rate unit regression: max={max(picks)}')
        need(max(picks)<10,f'Pick-rate distribution unexpectedly high for current source: max={max(picks)}')
    if bans:
        need(any(0 < x < 1 for x in bans),'Expected at least one sub-1% ban rate; parser may be rescaling small values')
    need(any(0 < x < 1 for x in picks),'Expected at least one sub-1% pick rate; parser may be rescaling small values')

if history_path.exists():
    try:
        hist=json.loads(history_path.read_text(encoding='utf-8'))
        need(hist.get('identity_version')==1,'History identity_version mismatch')
        need(hist.get('parser_version')==2,'History parser_version mismatch')
        need(hist.get('rate_unit')=='percentage_points','History rate_unit mismatch')
        snaps=hist.get('snapshots',[])
        need(len(snaps)>=1,'History must contain at least one corrected snapshot')
        for i,snap in enumerate(snaps):
            hs=snap.get('heroes',[])
            need(len(hs)==133,f'History snapshot {i} has {len(hs)} heroes instead of 133')
            for h in hs:
                need(h.get('key')==hero_key(h.get('name')),f'History key mismatch for {h.get("name")}')
                p=h.get('pick')
                need(isinstance(p,(int,float)) and 0<=p<=20,f'History pick-rate scale invalid for {h.get("name")}: {p}')
    except Exception as e:
        errors.append(f'Cannot validate meta-history.json: {e}')

for page in ['index.html','roster/index.html','trends/index.html','my-meta/index.html']:
    p=Path(page)
    need(p.exists(),f'Missing key surface: {page}')
    if p.exists():
        text=p.read_text(encoding='utf-8')
        need('DATA CONTRACT · % POINTS' in text,f'Data-contract label missing on {page}')
        need('puntos porcentuales' in text,f'Percentage-point explanation missing on {page}')
        need('Medición del proveedor' in text,f'Source measurement disclosure missing on {page}')

if errors:
    print('LIVE DATA CONTRACT VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Live data contract validation passed: parser v2, percentage-point rates, 133 heroes, source measurement timestamp, corrected history and visible provenance.')
