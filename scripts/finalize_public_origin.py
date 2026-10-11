from pathlib import Path
import re
from site_config import load_site_config, canonical_for
import generate_404

ROOT=Path('.')
CFG=load_site_config()
BASE=CFG['base_url']
NOINDEX=set(CFG['noindex_paths'])
LEGACY=[u for u in CFG.get('legacy_base_urls',[]) if u!=BASE]
TEXT_SUFFIXES={'.html','.xml','.txt','.json','.js','.webmanifest'}
SKIP_TOP={'.git','.github','scripts','_site'}


def is_public_text(path):
    if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    if path.parts and path.parts[0] in SKIP_TOP:
        return False
    if path.as_posix()=='data/site-config.json':
        return False
    return True

rewritten=0
for path in ROOT.rglob('*'):
    if not is_public_text(path):
        continue
    text=path.read_text(encoding='utf-8')
    updated=text
    for old in LEGACY:
        updated=updated.replace(old,BASE)
    if updated!=text:
        path.write_text(updated,encoding='utf-8')
        rewritten+=1

pages=[]
for path in ROOT.rglob('*.html'):
    if path.parts and path.parts[0] in SKIP_TOP:
        continue
    rel=path.as_posix()
    text=path.read_text(encoding='utf-8')
    if rel in NOINDEX or re.search(r'<meta\s+[^>]*name=["\']robots["\'][^>]*noindex',text,re.I):
        continue
    pages.append(rel)

pages=sorted(set(pages),key=lambda x:(x!='index.html',x))
urls=[canonical_for(p,BASE) for p in pages]
sitemap=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url in urls:
    sitemap.append(f'  <url><loc>{url}</loc></url>')
sitemap.append('</urlset>')
(ROOT/'sitemap.xml').write_text('\n'.join(sitemap)+'\n',encoding='utf-8')
(ROOT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n',encoding='utf-8')

cname=ROOT/'CNAME'
if CFG.get('custom_domain'):
    cname.write_text(CFG['custom_domain']+'\n',encoding='utf-8')
elif cname.exists():
    cname.unlink()

print(f'Public origin finalized: base={BASE}; custom_domain={CFG.get("custom_domain") or "none"}; indexable={len(urls)}; rewritten_files={rewritten}; noindex={len(NOINDEX)}; branded_404={Path("404.html").exists()}')
