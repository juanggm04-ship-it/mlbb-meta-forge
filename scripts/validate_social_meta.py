from pathlib import Path
import re, struct, sys, json
from site_config import load_site_config, canonical_for

CFG=load_site_config()
BASE=CFG['base_url']
CARD=Path('assets/social-card.png')
NOINDEX_PATHS=set(CFG['noindex_paths'])
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
def expected_url(p):
    return canonical_for(p,BASE)
need(CARD.exists(),'Social preview card missing')
if CARD.exists():
    data=CARD.read_bytes()
    need(data.startswith(b'\x89PNG\r\n\x1a\n'),'Social preview card is not PNG')
    if len(data)>=24:
        w,h=struct.unpack('>II',data[16:24]);need((w,h)==(1200,630),f'Social card dimensions are {w}x{h}, expected 1200x630')
    need(CARD.stat().st_size<=500*1024,f'Social card exceeds 500 KiB: {CARD.stat().st_size/1024:.1f} KiB')

pages=[p for p in Path('.').rglob('*.html') if '.git' not in p.parts and '_site' not in p.parts]
public=[];structured_ok=0;breadcrumb_ok=0;canonical_urls=set()
for p in pages:
    text=p.read_text(encoding='utf-8');rel=p.as_posix()
    if rel in NOINDEX_PATHS:
        need('content="noindex,nofollow"' in text,f'Noindex missing on {p}')
        need('id="mf-structured-data"' not in text,f'Noindex utility must not emit JSON-LD on {p}')
        need('rel="canonical"' not in text,f'Noindex utility must not emit canonical on {p}')
        continue
    public.append(p);expected=expected_url(p)
    need(text.count('id="mf-social-meta"')==1,f'Expected one social-meta marker on {p}')
    need(text.count('rel="canonical"')==1,f'Expected one canonical on {p}')
    need(text.count('id="mf-structured-data"')==1,f'Expected one JSON-LD block on {p}')
    for token,label in [
        ('property="og:title"','og:title'),('property="og:description"','og:description'),('property="og:url"','og:url'),
        ('property="og:image"','og:image'),('name="twitter:card"','twitter:card'),('name="twitter:title"','twitter:title'),
        ('name="twitter:description"','twitter:description'),('name="twitter:image"','twitter:image')]:
        need(token in text,f'{label} missing on {p}')
    m=re.search(r'<link id="mf-social-meta" rel="canonical" href="([^"]+)"',text)
    need(bool(m),f'Canonical value missing on {p}')
    if m:
        need(m.group(1)==expected,f'Canonical mismatch on {p}: {m.group(1)} != {expected}')
        canonical_urls.add(m.group(1))
    og=re.search(r'<meta property="og:url" content="([^"]+)"',text)
    need(bool(og),f'og:url value missing on {p}')
    if og: need(og.group(1)==expected,f'og:url mismatch on {p}: {og.group(1)} != {expected}')
    need(f'{BASE}assets/social-card.png' in text,f'Social image URL mismatch on {p}')
    j=re.search(r'<script id="mf-structured-data" type="application/ld\+json">(.*?)</script>',text,re.S)
    need(bool(j),f'JSON-LD payload missing on {p}')
    if j:
        try:
            payload=json.loads(j.group(1));graph=payload.get('@graph',[])
            website=[x for x in graph if x.get('@type')=='WebSite'];webpage=[x for x in graph if x.get('@type')=='WebPage'];crumb=[x for x in graph if x.get('@type')=='BreadcrumbList']
            need(payload.get('@context')=='https://schema.org',f'Wrong JSON-LD context on {p}')
            need(len(website)==1,f'Expected one WebSite node on {p}')
            need(len(webpage)==1,f'Expected one WebPage node on {p}')
            if website:
                need(website[0].get('url')==BASE,f'JSON-LD WebSite URL mismatch on {p}')
                need(website[0].get('name')==CFG['site_name'],f'JSON-LD site name mismatch on {p}')
            if webpage:
                need(webpage[0].get('url')==expected,f'JSON-LD WebPage URL mismatch on {p}')
                need(webpage[0].get('isPartOf',{}).get('@id')==BASE+'#website',f'JSON-LD site relation missing on {p}')
                need(webpage[0].get('about',{}).get('name')=='Mobile Legends: Bang Bang',f'JSON-LD MLBB subject missing on {p}')
            if rel=='index.html':
                need(len(crumb)==0,'Homepage should not emit a breadcrumb trail')
            else:
                need(len(crumb)==1,f'Expected one BreadcrumbList on {p}')
                if crumb:
                    items=crumb[0].get('itemListElement',[])
                    need(len(items)>=2,f'Breadcrumb too short on {p}')
                    if items:
                        need(items[0].get('item')==BASE,f'Breadcrumb must start at homepage on {p}')
                        need(items[-1].get('item')==expected,f'Breadcrumb must end at canonical URL on {p}')
                    breadcrumb_ok+=1
            structured_ok+=1
        except Exception as exc:
            errors.append(f'Invalid JSON-LD on {p}: {exc}')

stat_pages=list(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []
need(len(stat_pages)==133,f'Expected 133 live hero pages, got {len(stat_pages)}')
covered=sum(1 for p in stat_pages if 'property="og:title"' in p.read_text(encoding='utf-8') and 'rel="canonical"' in p.read_text(encoding='utf-8') and 'id="mf-structured-data"' in p.read_text(encoding='utf-8'))
need(covered==133,f'Social/structured metadata covers only {covered}/133 live hero pages')

sitemap=Path('sitemap.xml')
need(sitemap.exists(),'sitemap.xml missing')
if sitemap.exists():
    sitemap_urls=set(re.findall(r'<loc>(.*?)</loc>',sitemap.read_text(encoding='utf-8')))
    need(sitemap_urls==canonical_urls,f'Sitemap/canonical mismatch: sitemap={len(sitemap_urls)}, indexable={len(canonical_urls)}, missing={sorted(canonical_urls-sitemap_urls)[:3]}, extra={sorted(sitemap_urls-canonical_urls)[:3]}')
    for rel in NOINDEX_PATHS:
        need(canonical_for(rel,BASE) not in sitemap_urls,f'Noindex path must not appear in sitemap: {rel}')

if errors:
    print('SOCIAL META VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Social metadata validation passed: base={BASE}; public_pages={len(public)}; structured={structured_ok}; breadcrumbs={breadcrumb_ok}; live_hero_coverage={covered}/133; sitemap_exact={len(canonical_urls)}; noindex={len(NOINDEX)}; exact canonical/og:url paths, schema.org graph and 1200x630 social card are consistent.')

import validate_site_origin
