from pathlib import Path
import re, struct, sys

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
public=[]
for p in pages:
    text=p.read_text(encoding='utf-8')
    if p.as_posix() in ('offline.html','404.html'):
        need('content="noindex,nofollow"' in text,f'Noindex missing on {p}')
        continue
    public.append(p);expected=expected_url(p)
    need(text.count('id="mf-social-meta"')==1,f'Expected one social-meta marker on {p}')
    need(text.count('rel="canonical"')==1,f'Expected one canonical on {p}')
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

stat_pages=list(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []
need(len(stat_pages)==133,f'Expected 133 live hero pages, got {len(stat_pages)}')
covered=sum(1 for p in stat_pages if 'property="og:title"' in p.read_text(encoding='utf-8') and 'rel="canonical"' in p.read_text(encoding='utf-8'))
need(covered==133,f'Social metadata covers only {covered}/133 live hero pages')
if errors:
    print('SOCIAL META VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print(f'Social metadata validation passed: public_pages={len(public)}; live_hero_coverage={covered}/133; exact canonical/og:url paths and 1200x630 social card are consistent.')
