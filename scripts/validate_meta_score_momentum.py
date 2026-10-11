from pathlib import Path
import json,sys

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

score_path=Path('data/meta-score.json')
history_path=Path('data/meta-history.json')
score_history_path=Path('data/meta-score-history.json')
need(score_path.exists(),'meta-score.json missing')
need(history_path.exists(),'meta-history.json missing')
need(score_history_path.exists(),'meta-score-history.json missing')

if score_path.exists() and history_path.exists() and score_history_path.exists():
    score=json.loads(score_path.read_text(encoding='utf-8'))
    hist=json.loads(history_path.read_text(encoding='utf-8'))
    score_hist=json.loads(score_history_path.read_text(encoding='utf-8'))
    rows=score.get('heroes',[])
    snaps=hist.get('snapshots',[])
    score_snaps=score_hist.get('snapshots',[])
    need(score.get('version')==3,f'Meta Score version must be 3, found {score.get("version")}')
    need(score_hist.get('version')==2,f'Meta Score history version must be 2, found {score_hist.get("version")}')
    need(len(rows)==133,f'Expected 133 Meta Score rows, found {len(rows)}')
    need(score_hist.get('snapshot_count')==len(score_snaps),'Meta Score history snapshot_count does not match snapshots')
    need(len(score_snaps)==len(snaps),f'Meta Score history snapshot count {len(score_snaps)} differs from live history {len(snaps)}')
    need('patch or live WR/ban/pick changes semantically' in score_hist.get('history_rule',''),'Meta Score history semantic-snapshot rule missing')
    observed=[r for r in rows if r.get('momentum_observed')]
    neutral=[r for r in rows if not r.get('momentum_observed')]
    need(score.get('momentum_observed_count')==len(observed),'momentum_observed_count does not match rows')

    expected_history_status='waiting_for_real_change' if len(snaps)<2 else 'active'
    if len(snaps)<2:
        need(score.get('momentum_status')=='neutral_no_history',f'One-snapshot score must be neutral_no_history, found {score.get("momentum_status")}')
        need(score_hist.get('history_status')==expected_history_status,f'One-snapshot history must be {expected_history_status}, found {score_hist.get("history_status")}')
        need(len(observed)==0,f'Momentum must not be observed with one snapshot; found {len(observed)} observed rows')
        for r in neutral:
            need(r.get('momentum_raw') is None,f'Neutral momentum_raw must be null for {r.get("name")}')
            need(r.get('momentum_pct')==50.0,f'Neutral momentum percentile must be 50 for {r.get("name")}, found {r.get("momentum_pct")}')
    else:
        need(score.get('momentum_status') in ('observed','partial'),f'Two-plus snapshots must expose observed/partial momentum, found {score.get("momentum_status")}')
        need(score_hist.get('history_status')==expected_history_status,f'Two-plus snapshot history must be {expected_history_status}, found {score_hist.get("history_status")}')
        need(len(observed)>0,'Two-plus snapshots exist but no Meta Score momentum is observed')

    for page in ['roster/index.html','trends/index.html','my-meta/index.html']:
        p=Path(page); need(p.exists(),f'Missing Meta Score surface: {page}')
        if p.exists():
            text=p.read_text(encoding='utf-8')
            if len(snaps)<2:
                need('Momentum neutral' in text,f'Neutral momentum disclosure missing on {page}')

    trends=Path('trends/index.html')
    mymeta=Path('my-meta/index.html')
    for p in [trends,mymeta]:
        need(p.exists(),f'Missing history status surface: {p}')
        if p.exists():
            text=p.read_text(encoding='utf-8')
            need(f'data-history-snapshots="{len(snaps)}"' in text,f'History snapshot count missing/mismatched on {p}')
            need(f'data-history-status="{expected_history_status}"' in text,f'History readiness status missing/mismatched on {p}')
            if len(snaps)<2:
                need('1 snapshot real · esperando cambio real' in text,f'Human-readable waiting status missing on {p}')
            else:
                need('snapshots reales · historial activo' in text,f'Human-readable active status missing on {p}')

    home=Path('index.html')
    need(home.exists(),'Homepage missing for data-health history validation')
    if home.exists():
        text=home.read_text(encoding='utf-8')
        need('id="dataHealth"' in text,'Homepage data-health panel missing')
        need('id="dhHistory"' in text and '>HISTORIAL<' in text,'Homepage history cell missing')
        need(f'data-history-snapshots="{len(snaps)}"' in text,'Homepage history snapshot count differs from source history')
        need(f'data-history-status="{expected_history_status}"' in text,'Homepage history readiness status differs from Trends/My Meta')
        if len(snaps)<2:
            need('1 snapshot real' in text,'Homepage does not disclose the single real snapshot')
            need('espera un cambio semántico' in text,'Homepage does not explain why history is still waiting')
        else:
            need(f'{len(snaps)} snapshots' in text,'Homepage active history count missing')

    stat_pages=list(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []
    need(len(stat_pages)==133,f'Expected 133 stat pages, found {len(stat_pages)}')
    if len(snaps)<2:
        neutral_pages=sum(1 for p in stat_pages if 'Momentum · neutral' in p.read_text(encoding='utf-8'))
        need(neutral_pages==133,f'Neutral momentum label present on {neutral_pages}/133 stat pages')

if errors:
    print('META SCORE MOMENTUM VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Meta Score momentum/history validation passed: homepage, Trends and My Meta share one explicit snapshot-readiness contract.')
