from pathlib import Path
import hashlib, json, sys

ROOT=Path('.')
SITE=ROOT/'_site'
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

need(SITE.exists(),'_site artifact directory missing')
for name in ['index.html','privacy.html','terms.html','methodology.html','offline.html','manifest.webmanifest','robots.txt','sitemap.xml','sw.js']:
    need((SITE/name).exists(),f'Public artifact missing {name}')
for name in ['assets','data','heroes','stats','roster','explore','trends','compare','my-meta','status']:
    need((SITE/name).is_dir(),f'Public artifact missing directory {name}/')
need((SITE/'explore/index.html').exists(),'Meta Explorer page missing from public artifact')

bad=[p for p in SITE.rglob('*') if p.is_file() and (p.suffix.lower()=='.py' or '__pycache__' in p.parts)]
need(not bad,'Build/source Python leaked into public artifact: '+', '.join(str(p) for p in bad[:10]))
need(not (SITE/'scripts').exists(),'scripts/ leaked into public artifact')
need(not (SITE/'.github').exists(),'.github/ leaked into public artifact')

source_html=[p for p in ROOT.rglob('*.html') if '_site' not in p.parts and '.git' not in p.parts]
site_html=list(SITE.rglob('*.html'))
need(len(site_html)==len(source_html),f'HTML parity mismatch: source={len(source_html)}, artifact={len(site_html)}')
stat_pages=list((SITE/'stats/heroes').glob('*/index.html')) if (SITE/'stats/heroes').exists() else []
editorial_pages=list((SITE/'heroes').glob('*/index.html')) if (SITE/'heroes').exists() else []
need(len(stat_pages)==133,f'Expected 133 live hero pages in artifact, got {len(stat_pages)}')
need(len(editorial_pages)==34,f'Expected 34 editorial hero pages in artifact, got {len(editorial_pages)}')

for dest in [p for p in SITE.rglob('*') if p.is_file()]:
    rel=dest.relative_to(SITE);src=ROOT/rel
    need(src.exists(),f'Artifact file has no source counterpart: {rel}')
    if src.exists(): need(digest(src)==digest(dest),f'Artifact copy differs from validated source: {rel}')

required_data=['live-meta.json','meta-score.json','meta-score-history.json','build-info.json','product-release.json','integrity.json']
for name in required_data: need((SITE/'data'/name).exists(),f'Runtime data missing from artifact: data/{name}')

if (SITE/'data/build-info.json').exists() and (SITE/'data/product-release.json').exists():
    try:
        info=json.loads((SITE/'data/build-info.json').read_text(encoding='utf-8'))
        release=json.loads((SITE/'data/product-release.json').read_text(encoding='utf-8'))
        need((info.get('product_release') or {}).get('release_id')==release.get('release_id'),'Artifact build-info/product-release mismatch')
    except Exception as exc: errors.append(f'Invalid artifact product release metadata: {exc}')

integrity_path=SITE/'data/integrity.json'
if integrity_path.exists():
    try: integrity=json.loads(integrity_path.read_text(encoding='utf-8'))
    except Exception as exc: integrity={};errors.append(f'Invalid artifact integrity manifest: {exc}')
    entries=integrity.get('files') if isinstance(integrity.get('files'),dict) else {}
    for rel,item in entries.items():
        p=SITE/rel
        need(p.exists(),f'Integrity entry missing from _site: {rel}')
        if p.exists():
            need(item.get('bytes')==p.stat().st_size,f'Artifact integrity size mismatch: {rel}')
            need(item.get('sha256')==digest(p),f'Artifact integrity hash mismatch: {rel}')
    artifact_files=[p for p in SITE.rglob('*') if p.is_file() and p!=integrity_path]
    need(set(entries)=={p.relative_to(SITE).as_posix() for p in artifact_files},'Integrity manifest does not cover exactly every public artifact file except itself')

size=sum(p.stat().st_size for p in SITE.rglob('*') if p.is_file())
need(size<=25*1024*1024,f'Public artifact exceeds 25 MiB guardrail: {size/1024/1024:.2f} MiB')
if errors:
    print('PUBLIC ARTIFACT VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Public artifact validation passed: html={len(site_html)}; live=133; editorial=34; Explorer present; product-release present; size={size/1024/1024:.2f}MiB; exact integrity coverage; no Python/workflow build sources served.')
