from pathlib import Path
import re, html, struct, zlib, binascii

ROOT=Path('.')
BASE='https://juanggm04-ship-it.github.io/mlbb-meta-forge/'
CARD=Path('assets/social-card.png')
W,H=1200,630

def png_chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',binascii.crc32(kind+data)&0xffffffff)

def make_social_card():
    CARD.parent.mkdir(parents=True,exist_ok=True)
    raw=bytearray()
    for y in range(H):
        raw.append(0)
        for x in range(W):
            # Dark navy base with two soft esports glows.
            r,g,b=7,10,18
            d1=((x-210)**2+(y-130)**2)**0.5
            d2=((x-1010)**2+(y-500)**2)**0.5
            c1=max(0,1-d1/520)
            c2=max(0,1-d2/520)
            r=min(255,int(r+15*c1+42*c2))
            g=min(255,int(g+54*c1+18*c2))
            b=min(255,int(b+83*c1+72*c2))
            # Geometric MF monogram, no external font dependency.
            cyan=(70,230,255); violet=(139,92,255); gold=(242,194,85)
            col=None
            if 300<=x<342 and 205<=y<425: col=cyan
            elif 468<=x<510 and 205<=y<425: col=cyan
            elif 342<=x<384 and 205<=y<315 and abs((x-342)-(y-205)*.38)<18: col=cyan
            elif 426<=x<468 and 205<=y<315 and abs((468-x)-(y-205)*.38)<18: col=cyan
            elif 620<=x<662 and 205<=y<425: col=violet
            elif 662<=x<850 and 205<=y<247: col=violet
            elif 662<=x<815 and 300<=y<342: col=violet
            elif 300<=x<850 and 458<=y<466: col=gold
            if col: r,g,b=col
            raw.extend((r,g,b))
    ihdr=struct.pack('>IIBBBBB',W,H,8,2,0,0,0)
    data=b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',ihdr)+png_chunk(b'IDAT',zlib.compress(bytes(raw),9))+png_chunk(b'IEND',b'')
    CARD.write_bytes(data)

def canonical_for(path):
    rel=path.as_posix()
    if rel=='index.html': return BASE
    if rel.endswith('/index.html'): return BASE+rel[:-10]
    return BASE+rel

def title_of(text):
    m=re.search(r'<title>(.*?)</title>',text,re.I|re.S)
    return html.unescape(re.sub(r'<[^>]+>','',m.group(1)).strip()) if m else 'MLBB Meta Forge'

def description_of(text):
    m=re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',text,re.I|re.S)
    if not m:
        m=re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']\s*/?>',text,re.I|re.S)
    return html.unescape(m.group(1).strip()) if m else 'Meta, live stats, Hero Compare, Trends y Draft Coach para MLBB.'

def esc(v):
    return html.escape(v,quote=True)

make_social_card()
changed=0; indexed=0; noindexed=0
for path in ROOT.rglob('*.html'):
    if '.git' in path.parts: continue
    text=path.read_text(encoding='utf-8')
    if 'id="mf-social-meta"' in text: continue
    rel=path.as_posix()
    if rel in ('offline.html','404.html'):
        if 'name="robots"' not in text:
            text=text.replace('</head>','<meta id="mf-social-meta" name="robots" content="noindex,nofollow"></head>',1)
        else:
            text=text.replace('</head>','<meta id="mf-social-meta" name="referrer" content="no-referrer"></head>',1)
        path.write_text(text,encoding='utf-8');changed+=1;noindexed+=1
        continue
    title=title_of(text);desc=description_of(text);canonical=canonical_for(path)
    # Keep one canonical source of truth even if a generator already added one.
    text=re.sub(r'<link\s+rel=["\']canonical["\'][^>]*>','',text,flags=re.I)
    block=(f'<link id="mf-social-meta" rel="canonical" href="{esc(canonical)}">'
           f'<meta property="og:site_name" content="MLBB Meta Forge">'
           f'<meta property="og:type" content="website">'
           f'<meta property="og:title" content="{esc(title)}">'
           f'<meta property="og:description" content="{esc(desc)}">'
           f'<meta property="og:url" content="{esc(canonical)}">'
           f'<meta property="og:image" content="{BASE}assets/social-card.png">'
           f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
           f'<meta name="twitter:card" content="summary_large_image">'
           f'<meta name="twitter:title" content="{esc(title)}">'
           f'<meta name="twitter:description" content="{esc(desc)}">'
           f'<meta name="twitter:image" content="{BASE}assets/social-card.png">'
           f'<meta name="referrer" content="strict-origin-when-cross-origin">')
    text=text.replace('</head>',block+'</head>',1)
    path.write_text(text,encoding='utf-8');changed+=1;indexed+=1
print(f'Social metadata injected: pages={changed}; indexable={indexed}; noindex={noindexed}; social_card={CARD.stat().st_size/1024:.1f}KiB')
