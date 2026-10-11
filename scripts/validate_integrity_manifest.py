from pathlib import Path
import hashlib, json, subprocess, sys

ROOT=Path('.')
MANIFEST=ROOT/'data/integrity.json'
ROOT_FILES=['index.html','privacy.html','terms.html','methodology.html','offline.html','manifest.webmanifest','robots.txt','sitemap.xml','sw.js']
if Path('404.html').exists(): ROOT_FILES.append('404.html')
PUBLIC_DIRS=['assets','data','heroes','stats','roster','explore','trends','compare','my-meta','status','repair']
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def expected_files():
    found=[]
    for name in ROOT_FILES:
        p=ROOT/name
        if p.exists(): found.append(p)
    for name in PUBLIC_DIRS:
        base=ROOT/name
        if base.exists(): found.extend(p for p in base.rglob('*') if p.is_file() and p!=MANIFEST)
    return {p.as_posix():p for p in found}

need(MANIFEST.exists(),'data/integrity.json missing')
manifest={}
if MANIFEST.exists():
    try: manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    except Exception as exc: errors.append(f'Invalid integrity JSON: {exc}')
need(manifest.get('schema_version')==1,'Integrity schema_version must be 1')
need(manifest.get('algorithm')=='sha256','Integrity algorithm must be sha256')
try: head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
except Exception as exc: head=None;errors.append(f'Cannot resolve git HEAD: {exc}')
if head: need(manifest.get('build_sha')==head,f'Integrity build SHA mismatch: {manifest.get("build_sha")} != {head}')
files=manifest.get('files') if isinstance(manifest.get('files'),dict) else {}
expected=expected_files()
need(set(files)==set(expected),f'Integrity coverage mismatch: manifest={len(files)} expected={len(expected)} missing={sorted(set(expected)-set(files))[:5]} extra={sorted(set(files)-set(expected))[:5]}')
actual_total=0
for rel,path in expected.items():
    actual_total+=path.stat().st_size
    item=files.get(rel,{})
    need(item.get('bytes')==path.stat().st_size,f'Size mismatch for {rel}')
    need(item.get('sha256')==sha256(path),f'SHA-256 mismatch for {rel}')
need(manifest.get('file_count')==len(expected),f'Integrity file_count mismatch: {manifest.get("file_count")} != {len(expected)}')
need(manifest.get('total_bytes')==actual_total,f'Integrity total_bytes mismatch: {manifest.get("total_bytes")} != {actual_total}')
for rel in ['index.html','explore/index.html','status/index.html','repair/index.html','data/live-meta.json','data/meta-score.json','data/build-info.json','sw.js','assets/social-card.png']:
    need(rel in files,f'Critical integrity entry missing: {rel}')
status=Path('status/index.html').read_text(encoding='utf-8') if Path('status/index.html').exists() else ''
need('../data/integrity.json' in status,'Status page does not link to integrity manifest')
need('../repair/' in status,'Status page does not link to repair utility')
need(len(expected)>=196,f'Integrity manifest unexpectedly small after repair utility: {len(expected)} files')
if errors:
    print('INTEGRITY MANIFEST VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Integrity validation passed: build={head[:12] if head else "unknown"}; files={len(expected)}; Explorer + repair covered; total={actual_total/1024/1024:.2f}MiB; exact SHA-256 coverage.')
