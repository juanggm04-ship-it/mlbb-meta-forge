from pathlib import Path
import re, html, struct, zlib, binascii, json
from site_config import load_site_config
import finalize_public_origin

ROOT=Path('.')
CFG=load_site_config()
BASE=CFG['base_url']
SITE_NAME=CFG['site_name']
CARD=Path('assets/social-card.png')
W,H=1200,630
LIVE=Path('data/live-meta.json')
NOINDEX_PATHS=set(CFG['noindex_paths'])


def png_chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',binascii.crc32(kind+data)&0xffffffff)

def make_social_card():
    CARD.parent.mkdir(parents=True,exist_ok=True)
    raw=bytearray()
    for y in range(H):
        raw.append(0)
        for x in range(W):
            r,g,b=7,10,18
            d1=((x-210)**2+(y-130)**2)**0.5
            d2=((x-1010)**2+(y-500)**2)**0.5
            c1=max(0,1-d1/520)
            c2=max(0,1-d2/520)
            r=min(255,int(r+15*c1+42*c2))
            g=min(255,int(g+54*c1+18*c2))
            b=min(255,int(b+83*c1+72*c2))
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
    return html.unescape(re.sub(r'<[^>]+>','',m.group(1)).strip()) if m else SITE_NAME

def description_of(text):
    m=re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>',text,re.I|re.S)
    if not m:
        m=re.search(r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']\s*/?>',text,re.I|re.S)
    return html.unescape(m.group(1).strip()) if m else 'Meta, live stats, Hero Compare, Trends y Draft Coach para MLBB.'

def esc(v):
    return html.escape(v,quote=True)

def breadcrumb_name(segment):
    known={
        'roster':'Live Roster','explore':'Meta Explorer','trends':'Trends','compare':'Hero Compare',
        'my-meta':'My Meta','methodology.html':'Metodología','status':'Estado','stats':'Estadísticas',
        'heroes':'Héroes','privacy.html':'Privacidad','terms.html':'Términos'
    }
    return known.get(segment,segment.replace('.html','').replace('-',' ').title())

def breadcrumb_graph(path,canonical):
    rel=path.as_posix()
    if rel=='index.html': return None
    parts=rel.split('/')
    if parts[-1]=='index.html':parts=parts[:-1]
    items=[{'@type':'ListItem','position':1,'name':'Meta Forge','item':BASE}]
    if len(parts)>=3 and parts[0]=='stats' and parts[1]=='heroes':
        items.append({'@type':'ListItem','position':2,'name':'Live Roster','item':BASE+'roster/'})
        items.append({'@type':'ListItem','position':3,'name':breadcrumb_name(parts[2]),'item':canonical})
    elif len(parts)>=2 and parts[0]=='heroes':
        items.append({'@type':'ListItem','position':2,'name':'Héroes','item':BASE+'heroes/'})
        if len(parts)>1:items.append({'@type':'ListItem','position':3,'name':breadcrumb_name(parts[1]),'item':canonical})
    else:
        current=BASE
        for i,segment in enumerate(parts,2):
            current+=segment+('/' if '.' not in segment else '')
            items.append({'@type':'ListItem','position':i,'name':breadcrumb_name(segment),'item':canonical if i==len(parts)+1 else current})
    return {'@type':'BreadcrumbList','@id':canonical+'#breadcrumb','itemListElement':items}

def structured_graph(path,title,desc,canonical,modified):
    website={
        '@type':'WebSite','@id':BASE+'#website','url':BASE,'name':SITE_NAME,'inLanguage':CFG['locale'],
        'description':'Herramientas estadísticas y editoriales para explorar el meta de Mobile Legends: Bang Bang.'
    }
    webpage={
        '@type':'WebPage','@id':canonical+'#webpage','url':canonical,'name':title,'description':desc,
        'inLanguage':CFG['locale'],'isPartOf':{'@id':BASE+'#website'},
        'about':{'@type':'VideoGame','name':'Mobile Legends: Bang Bang'}
    }
    if modified:webpage['dateModified']=modified
    crumb=breadcrumb_graph(path,canonical)
    graph=[website,webpage]
    if crumb:
        webpage['breadcrumb']={'@id':crumb['@id']}
        graph.append(crumb)
    return {'@context':'https://schema.org','@graph':graph}

make_social_card()
modified=None
if LIVE.exists():
    try:
        live=json.loads(LIVE.read_text(encoding='utf-8'));modified=live.get('source_updated') or live.get('fetched_at')
    except Exception:
        modified=None
changed=0; indexed=0; noindexed=0; structured=0
for path in ROOT.rglob('*.html'):
    if '.git' in path.parts or '_site' in path.parts: continue
    text=path.read_text(encoding='utf-8')
    if 'id="mf-social-meta"' in text: continue
    rel=path.as_posix()
    if rel in NOINDEX_PATHS:
        text=re.sub(r'<meta\s+name=["\']robots["\'][^>]*>','',text,flags=re.I)
        text=text.replace('</head>','<meta id="mf-social-meta" name="robots" content="noindex,nofollow"><meta name="referrer" content="no-referrer"></head>',1)
        path.write_text(text,encoding='utf-8');changed+=1;noindexed+=1
        continue
    title=title_of(text);desc=description_of(text);canonical=canonical_for(path)
    text=re.sub(r'<link\s+rel=["\']canonical["\'][^>]*>','',text,flags=re.I)
    block=(f'<link id="mf-social-meta" rel="canonical" href="{esc(canonical)}">'
           f'<meta property="og:site_name" content="{esc(SITE_NAME)}">'
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
    graph=structured_graph(path,title,desc,canonical,modified)
    jsonld=json.dumps(graph,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    block+=f'<script id="mf-structured-data" type="application/ld+json">{jsonld}</script>'
    text=text.replace('</head>',block+'</head>',1)
    path.write_text(text,encoding='utf-8');changed+=1;indexed+=1;structured+=1
print(f'Social metadata injected: pages={changed}; indexable={indexed}; noindex={noindexed}; structured={structured}; base={BASE}; social_card={CARD.stat().st_size/1024:.1f}KiB')
