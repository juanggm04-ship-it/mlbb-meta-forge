from pathlib import Path
import re, struct, sys, json

BASE='https://juanggm04-ship-it.github.io/mlbb-meta-forge/'
CARD=Path('assets/social-card.png')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
def expected_url(p):
    rel=p.as_posix()
    if rel=='index.html': return BASE
    if rel.endswith('/index.html'): return BASE+rel[:-10]
    return BASE+rel
need(CARD.exists(),'Social preview card missing')
if CARD.exists():
    data=CARD.read_bytes()
    need(data.startswith(b'\x89PNG\r\n\x1a\n'),'Social preview card is not PNG')
    if len(data)>=24:
        w,h=struct.unpack('>II',data[16:24]);need((w,h)==(1200,630),f'Social card dimensions are {w}x{h}, expected 1200x630')
    need(CARD.stat().st_size<=500*1024,f'Social card exceeds 500 KiB: {CARD.stat().st_size/1024:.1f} KiB')

pages=[p for p in Path('.').rglob('*.html') if '.git' not in p.parts]
public=[];structured_ok=0;breadcrumb_ok=0
for p in pages:
    text=p.read_text(encoding='utf-8')
    if p.as_posix() in ('offline.html','404.html'):
        need('content="noindex,nofollow"' in text,f'Noindex missing on {p}')
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
    if m: need(m.group(1)==expected,f'Canonical mismatch on {p}: {m.group(1)} != {expected}')
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
            if webpage:
                need(webpage[0].get('url')==expected,f'JSON-LD WebPage URL mismatch on {p}')
                need(webpage[0].get('isPartOf',{}).get('@id')==BASE+'#website',f'JSON-LD site relation missing on {p}')
                need(webpage[0].get('about',{}).get('name')=='Mobile Legends: Bang Bang',f'JSON-LD MLBB subject missing on {p}')
            if p.as_posix()=='index.html':
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
if errors:
    print('SOCIAL META VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Social metadata validation passed: public_pages={len(public)}; structured={structured_ok}; breadcrumbs={breadcrumb_ok}; live_hero_coverage={covered}/133; exact canonical/og:url paths, schema.org graph and 1200x630 social card are consistent.')
