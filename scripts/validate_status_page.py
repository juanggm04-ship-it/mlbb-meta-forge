from pathlib import Path
import json, os, subprocess, sys

PAGE=Path('status/index.html')
INFO=Path('data/build-info.json')
LIVE=Path('data/live-meta.json')
CATALOG=Path('data/hero-catalog.json')
HISTORY=Path('data/meta-history.json')
SCORE=Path('data/meta-score.json')
RELEASE=Path('data/product-release.json')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
for p in (PAGE,INFO,LIVE,CATALOG,HISTORY,SCORE,RELEASE): need(p.exists(),f'Missing status dependency: {p}')
if not errors:
    info=json.loads(INFO.read_text(encoding='utf-8'))
    live=json.loads(LIVE.read_text(encoding='utf-8'))
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    history=json.loads(HISTORY.read_text(encoding='utf-8'))
    score=json.loads(SCORE.read_text(encoding='utf-8'))
    release=json.loads(RELEASE.read_text(encoding='utf-8'))
    live_count=len([h for h in live.get('heroes',[]) if h.get('name')])
    editorial_count=len([h for h in catalog.get('heroes',[]) if h.get('name')])
    points=len(history.get('snapshots',[])) if isinstance(history,dict) else 0
    observed=sum(1 for h in score.get('heroes',[]) if h.get('momentum_observed') is True)
    need(info.get('schema_version')==1,'build-info schema version mismatch')
    need(info.get('live_heroes')==live_count==133,f'Live coverage mismatch: info={info.get("live_heroes")}, actual={live_count}')
    need(info.get('editorial_heroes')==editorial_count==34,f'Editorial coverage mismatch: info={info.get("editorial_heroes")}, actual={editorial_count}')
    need(info.get('patch')==live.get('patch'),'Patch mismatch between build-info and live-meta')
    need(info.get('source_updated')==live.get('source_updated'),'source_updated mismatch')
    need(info.get('fetched_at')==live.get('fetched_at'),'fetched_at mismatch')
    need(info.get('history_points')==points,'History point count mismatch')
    need(info.get('momentum_observed_heroes')==observed,'Momentum observed count mismatch')
    expected_ready=points>=2 and observed>0
    need(info.get('history_ready') is expected_ready,'history_ready does not match real readiness')
    need(info.get('rate_unit')=='percentage_points','Status rate unit must be percentage_points')
    product=info.get('product_release') or {}
    need(product.get('release_id')==release.get('release_id'),'Product release id mismatch in build-info')
    need(product.get('title')==release.get('title'),'Product release title mismatch in build-info')
    need(product.get('published')==release.get('published'),'Product release date mismatch in build-info')
    need(product.get('highlights')==release.get('highlights'),'Product release highlights mismatch in build-info')
    try: head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    except Exception: head=os.getenv('GITHUB_SHA')
    if head: need(info.get('build_sha')==head,f'Build SHA mismatch: {info.get("build_sha")} != {head}')
    text=PAGE.read_text(encoding='utf-8')
    for token,msg in [
        ('BUILD + DATA STATUS','Status hero missing'),
        ('PRODUCT RELEASE','Product release section missing'),
        (release.get('release_id','__missing__'),'Product release id missing from status page'),
        ('TRES RELOJES DE DATOS Y BUILD','Freshness clock explanation missing'),
        ('Medición informada por la fuente','Source measurement explanation missing'),
        ('Última consulta validada por Meta Forge','Fetch-time explanation missing'),
        ('Build publicado','Build-time explanation missing'),
        ('../data/build-info.json','Machine-readable build-info link missing'),
        ('../data/product-release.json','Machine-readable product release link missing'),
        ('Si la fuente no cambia WR, ban, pick o patch, no se inventa un nuevo punto histórico.','Semantic-history disclosure missing')]:
        need(token in text,msg)
    need('https://juanggm04-ship-it.github.io/mlbb-meta-forge/status/' in Path('sitemap.xml').read_text(encoding='utf-8'),'Status page missing from sitemap')
if errors:
    print('STATUS VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Status validation passed: build={info.get("build_short")}; release={release.get("release_id")}; live=133; editorial=34; history={info.get("history_points")}; observed={info.get("momentum_observed_heroes")}; ready={info.get("history_ready")}.')
