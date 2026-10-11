from pathlib import Path
import json,sys

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

score_path=Path('data/meta-score.json')
history_path=Path('data/meta-history.json')
need(score_path.exists(),'meta-score.json missing')
need(history_path.exists(),'meta-history.json missing')

if score_path.exists() and history_path.exists():
    score=json.loads(score_path.read_text(encoding='utf-8'))
    hist=json.loads(history_path.read_text(encoding='utf-8'))
    rows=score.get('heroes',[])
    snaps=hist.get('snapshots',[])
    need(score.get('version')==3,f'Meta Score version must be 3, found {score.get("version")}')
    need(len(rows)==133,f'Expected 133 Meta Score rows, found {len(rows)}')
    observed=[r for r in rows if r.get('momentum_observed')]
    neutral=[r for r in rows if not r.get('momentum_observed')]
    need(score.get('momentum_observed_count')==len(observed),'momentum_observed_count does not match rows')

    if len(snaps)<2:
        need(score.get('momentum_status')=='neutral_no_history',f'One-snapshot score must be neutral_no_history, found {score.get("momentum_status")}')
        need(len(observed)==0,f'Momentum must not be observed with one snapshot; found {len(observed)} observed rows')
        for r in neutral:
            need(r.get('momentum_raw') is None,f'Neutral momentum_raw must be null for {r.get("name")}')
            need(r.get('momentum_pct')==50.0,f'Neutral momentum percentile must be 50 for {r.get("name")}, found {r.get("momentum_pct")}')
    else:
        need(score.get('momentum_status') in ('observed','partial'),f'Two-plus snapshots must expose observed/partial momentum, found {score.get("momentum_status")}')
        need(len(observed)>0,'Two-plus snapshots exist but no Meta Score momentum is observed')

    for page in ['roster/index.html','trends/index.html','my-meta/index.html']:
        p=Path(page); need(p.exists(),f'Missing Meta Score surface: {page}')
        if p.exists():
            text=p.read_text(encoding='utf-8')
            if len(snaps)<2:
                need('Momentum neutral' in text,f'Neutral momentum disclosure missing on {page}')

    stat_pages=list(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []
    need(len(stat_pages)==133,f'Expected 133 stat pages, found {len(stat_pages)}')
    if len(snaps)<2:
        neutral_pages=sum(1 for p in stat_pages if 'Momentum · neutral' in p.read_text(encoding='utf-8'))
        need(neutral_pages==133,f'Neutral momentum label present on {neutral_pages}/133 stat pages')

if errors:
    print('META SCORE MOMENTUM VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Meta Score momentum validation passed: unavailable history is explicitly neutral and future observed momentum is contract-checked.')
