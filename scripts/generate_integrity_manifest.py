from pathlib import Path
import datetime, hashlib, json, subprocess

ROOT=Path('.')
OUT=ROOT/'data/integrity.json'
ROOT_FILES=['index.html','privacy.html','terms.html','methodology.html','offline.html','manifest.webmanifest','robots.txt','sitemap.xml','sw.js']
if Path('404.html').exists(): ROOT_FILES.append('404.html')
PUBLIC_DIRS=['assets','data','heroes','stats','roster','explore','trends','compare','my-meta','status','repair']

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def public_files():
    found=[]
    for name in ROOT_FILES:
        p=ROOT/name
        if not p.exists(): raise RuntimeError(f'Integrity dependency missing: {name}')
        found.append(p)
    for name in PUBLIC_DIRS:
        base=ROOT/name
        if not base.exists(): raise RuntimeError(f'Integrity public directory missing: {name}')
        found.extend(p for p in base.rglob('*') if p.is_file() and p!=OUT)
    unique={p.as_posix():p for p in found}
    return [unique[k] for k in sorted(unique)]

try: build_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
except Exception as exc: raise RuntimeError(f'Cannot resolve git HEAD for integrity manifest: {exc}')
files=public_files()
entries={p.as_posix():{'sha256':sha256(p),'bytes':p.stat().st_size} for p in files}
manifest={
    'schema_version':1,
    'algorithm':'sha256',
    'build_sha':build_sha,
    'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'file_count':len(entries),
    'total_bytes':sum(v['bytes'] for v in entries.values()),
    'files':entries,
}
OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
print(f'Integrity manifest generated: build={build_sha[:12]}; files={len(entries)}; bytes={manifest["total_bytes"]}; explorer_covered=true; repair_covered=true; output={OUT}')
