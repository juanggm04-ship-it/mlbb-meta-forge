from pathlib import Path
import shutil

ROOT=Path('.')
SITE=ROOT/'_site'
if SITE.exists(): shutil.rmtree(SITE)
SITE.mkdir()

root_files=['index.html','privacy.html','terms.html','methodology.html','offline.html','manifest.webmanifest','robots.txt','sitemap.xml','sw.js']
if Path('404.html').exists(): root_files.append('404.html')
public_dirs=['assets','data','heroes','stats','roster','trends','compare','my-meta','status']

for name in root_files:
    src=ROOT/name
    if not src.exists(): raise RuntimeError(f'Public root file missing before artifact preparation: {name}')
    shutil.copy2(src,SITE/name)
for name in public_dirs:
    src=ROOT/name
    if not src.exists(): raise RuntimeError(f'Public directory missing before artifact preparation: {name}')
    shutil.copytree(src,SITE/name)

files=[p for p in SITE.rglob('*') if p.is_file()]
html_count=sum(1 for p in files if p.suffix.lower()=='.html')
size=sum(p.stat().st_size for p in files)
print(f'Prepared public Pages artifact: files={len(files)}; html={html_count}; size={size/1024/1024:.2f}MiB; dirs={len(public_dirs)}; build_sources_excluded=true')
