from pathlib import Path
import re, sys
from site_config import load_site_config, canonical_for

ROOT=Path('.')
CFG=load_site_config()
BASE=CFG['base_url']
NOINDEX=set(CFG['noindex_paths'])
LEGACY=[u for u in CFG.get('legacy_base_urls',[]) if u!=BASE]
errors=[]

def need(cond,msg):
    if not cond: errors.append(msg)

robots=Path('robots.txt')
sitemap=Path('sitemap.xml')
cname=Path('CNAME')
need(robots.exists(),'robots.txt missing')
need(sitemap.exists(),'sitemap.xml missing')
if robots.exists():
    text=robots.read_text(encoding='utf-8')
    need(f'Sitemap: {BASE}sitemap.xml' in text,'robots.txt sitemap URL does not match configured base URL')
if sitemap.exists():
    text=sitemap.read_text(encoding='utf-8')
    urls=set(re.findall(r'<loc>(.*?)</loc>',text))
else:
    urls=set()

if CFG.get('custom_domain'):
    need(cname.exists(),'Custom domain configured but CNAME file is missing')
    if cname.exists():
        need(cname.read_text(encoding='utf-8').strip()==CFG['custom_domain'],'CNAME does not match configured custom domain')
else:
    need(not cname.exists(),'CNAME exists while custom_domain is not configured')

pages=[]
for path in ROOT.rglob('*.html'):
    if path.parts and path.parts[0] in {'.git','.github','scripts','_site'}:
        continue
    rel=path.as_posix();html=path.read_text(encoding='utf-8')
    if rel in NOINDEX or re.search(r'<meta\s+[^>]*name=["\']robots["\'][^>]*noindex',html,re.I):
        continue
    pages.append(rel)
expected={canonical_for(p,BASE) for p in pages}
need(urls==expected,f'Sitemap differs from configured indexable set: sitemap={len(urls)}, expected={len(expected)}, missing={sorted(expected-urls)[:3]}, extra={sorted(urls-expected)[:3]}')

for rel in NOINDEX:
    need(canonical_for(rel,BASE) not in urls,f'Noindex path leaked into sitemap: {rel}')

stale=[]
scan=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in {'.html','.xml','.txt','.js','.webmanifest'}]
for path in scan:
    if path.parts and path.parts[0] in {'.git','.github','scripts','_site'}:
        continue
    text=path.read_text(encoding='utf-8')
    for old in LEGACY:
        if old in text:
            stale.append(f'{path}:{old}')
need(not stale,f'Stale legacy public origin found after finalization: {stale[:5]}')

if errors:
    print('SITE ORIGIN VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Site origin validation passed: base={BASE}; custom_domain={CFG.get("custom_domain") or "none"}; cname={cname.exists()}; indexable={len(expected)}; noindex={len(NOINDEX)}; stale_legacy_urls=0.')
