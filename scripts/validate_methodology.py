from pathlib import Path
import json,sys,html

errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

LIVE=Path('data/live-meta.json')
HISTORY=Path('data/meta-history.json')
SCORE=Path('data/meta-score.json')
SCORE_HISTORY=Path('data/meta-score-history.json')
CAT=Path('data/hero-catalog.json')
METHOD=Path('methodology.html')
SITEMAP=Path('sitemap.xml')

for p in [LIVE,HISTORY,SCORE,SCORE_HISTORY,CAT,METHOD,SITEMAP]:
    need(p.exists(),f'Methodology validation dependency missing: {p}')

if all(p.exists() for p in [LIVE,HISTORY,SCORE,SCORE_HISTORY,CAT,METHOD,SITEMAP]):
    live=json.loads(LIVE.read_text(encoding='utf-8'))
    history=json.loads(HISTORY.read_text(encoding='utf-8'))
    score=json.loads(SCORE.read_text(encoding='utf-8'))
    score_history=json.loads(SCORE_HISTORY.read_text(encoding='utf-8'))
    catalog=json.loads(CAT.read_text(encoding='utf-8'))
    page=METHOD.read_text(encoding='utf-8')
    snapshots=len(history.get('snapshots',[]))
    history_status=score_history.get('history_status')

    attrs={
        'data-parser-version':str(live.get('parser_version')),
        'data-rate-unit':str(live.get('rate_unit')),
        'data-live-heroes':str(len(live.get('heroes',[]))),
        'data-editorial-heroes':str(len(catalog.get('heroes',[]))),
        'data-history-snapshots':str(snapshots),
        'data-history-status':str(history_status),
        'data-momentum-status':str(score.get('momentum_status')),
        'data-patch':str(live.get('patch')),
    }
    for key,value in attrs.items():
        need(f'{key}="{html.escape(value,quote=True)}"' in page,f'Methodology {key} does not match current data: {value}')

    for token in [
        'key</code> · <code>name</code> · <code>wr</code> · <code>ban</code> · <code>pick',
        'puntos porcentuales',
        'El snapshot live no guarda tier, línea, rol, counters ni sinergias',
        'Corrección del parser v2',
        '0.65% podía representarse erróneamente como 65%',
        'No se fabricaron deltas',
        'Historial semántico',
        'Meta Score',
        'No es tier, probabilidad de victoria, counter score ni ranking oficial',
        'El proveedor público no se presenta como API oficial',
        'tier editorial no es un tier oficial',
    ]:
        need(token in page,f'Methodology missing required transparency text: {token}')

    need(str(score.get('formula')) in page,'Methodology Meta Score formula differs from generated score')
    need(str(score.get('momentum_formula')) in page,'Methodology momentum formula differs from generated score')
    need('/methodology.html' in SITEMAP.read_text(encoding='utf-8'),'Sitemap missing methodology.html')

    for surface in ['index.html','roster/index.html','trends/index.html','my-meta/index.html']:
        p=Path(surface)
        need(p.exists(),f'Key surface missing: {surface}')
        if p.exists():
            text=p.read_text(encoding='utf-8')
            need('data-methodology-link' in text,f'Methodology link missing from provenance on {surface}')
            need('/mlbb-meta-forge/methodology.html' in text,f'Methodology URL missing from {surface}')

if errors:
    print('METHODOLOGY VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Methodology validation passed: live schema, units, parser correction, history readiness, Meta Score formula and provenance links match current build.')
