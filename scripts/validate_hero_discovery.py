from pathlib import Path
import json, re, html, sys
from hero_identity import hero_key

LIVE=Path('data/live-meta.json'); SCORE=Path('data/meta-score.json'); ROOT=Path('stats/heroes'); CATALOG=Path('data/hero-catalog.json')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

for p in (LIVE,SCORE,CATALOG): need(p.exists(),f'Missing dependency: {p}')
if not all(p.exists() for p in (LIVE,SCORE,CATALOG)):
    for e in errors: print('- '+e)
    sys.exit(1)

live=json.loads(LIVE.read_text(encoding='utf-8')); score=json.loads(SCORE.read_text(encoding='utf-8')); catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
heroes=live.get('heroes',[]); scores=score.get('heroes',[])
need(len(heroes)==133,f'Expected 133 live rows, got {len(heroes)}')
need(len(scores)==133,f'Expected 133 score rows, got {len(scores)}')
live_by={hero_key(h['name']):h for h in heroes if h.get('name')}; score_by={hero_key(h['name']):h for h in scores if h.get('name')}
patch=str(live.get('patch') or 'actual'); updated=str(live.get('updated') or live.get('source_updated') or '').split('T')[0] or 'reciente'
pages=sorted(ROOT.glob('*/index.html')) if ROOT.exists() else []
need(len(pages)==133,f'Expected 133 stat pages, got {len(pages)}')
titles=[]; descriptions=[]; editorial_checked=0

def pct(v): return f'{float(v):.2f}%'

def extract(pattern,text):
    m=re.search(pattern,text,re.S|re.I)
    return html.unescape(m.group(1).strip()) if m else None

for page in pages:
    text=page.read_text(encoding='utf-8')
    name=extract(r'<h1>(.*?)</h1>',text)
    if not name:
        errors.append(f'{page}: h1 missing'); continue
    name=re.sub(r'<[^>]+>','',name).strip(); key=hero_key(name); row=live_by.get(key); sr=score_by.get(key)
    if not row or not sr:
        errors.append(f'{page}: unresolved live/score row for {name}'); continue
    wr=pct(row['wr']); ban=pct(row['ban']); pick=pct(row['pick']); ms=float(sr['score']); rank=int(sr['rank'])
    expected_title=f'{name} MLBB Win Rate {wr} · Ban {ban} | Meta Forge'
    expected_desc=f'{name} en MLBB patch {patch}: win rate {wr}, ban rate {ban}, pick rate {pick} y Meta Score {ms:.1f} (#{rank}/133). Datos live actualizados {updated}.'
    title=extract(r'<title>(.*?)</title>',text); desc=extract(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',text)
    need(title==expected_title,f'{page}: title mismatch')
    need(desc==expected_desc,f'{page}: description mismatch')
    if title: titles.append(title); need(len(title)<=78,f'{page}: title exceeds 78 chars')
    if desc: descriptions.append(desc); need(100<=len(desc)<=190,f'{page}: description length {len(desc)} outside 100-190')
    need(text.count('id="heroSearchSummary"')==1,f'{page}: discovery summary missing/duplicated')
    need(text.count('id="heroShareButton"')==1,f'{page}: share button missing/duplicated')
    need(text.count('id="heroShareStatus"')==1,f'{page}: share status missing/duplicated')
    need(text.count('id="hero-discovery-script"')==1,f'{page}: discovery runtime missing/duplicated')
    need(f'{wr} de win rate' in text and f'{ban} de ban rate' in text and f'{pick} de pick rate' in text,f'{page}: visible live-stat summary mismatch')
    need('El Meta Score no es un tier ni una probabilidad de victoria' in text,f'{page}: Meta Score disclosure missing')
    script_match=re.search(r'<script id="hero-discovery-script">(.*?)</script>',text,re.S)
    if script_match:
        runtime=script_match.group(1)
        need('navigator.share' in runtime and 'navigator.clipboard' in runtime,f'{page}: share/copy fallback missing')
        need('fetch(' not in runtime and 'XMLHttpRequest' not in runtime,f'{page}: discovery runtime must not send network requests')
    editorial_page=Path('heroes')/page.parent.name/'index.html'
    if editorial_page.exists():
        editorial_title=extract(r'<title>(.*?)</title>',editorial_page.read_text(encoding='utf-8'))
        need(editorial_title!=title,f'{page}: live title collides with editorial title')
        editorial_checked+=1

need(len(set(titles))==133,f'Expected 133 unique live-stat titles, got {len(set(titles))}')
need(len(set(descriptions))==133,f'Expected 133 unique live-stat descriptions, got {len(set(descriptions))}')
need(editorial_checked==34,f'Expected 34 live/editorial intent checks, got {editorial_checked}')

if errors:
    print('HERO DISCOVERY VALIDATION FAILED')
    for e in errors[:80]: print('- '+e)
    if len(errors)>80: print(f'- ... {len(errors)-80} more errors')
    sys.exit(1)
print('Hero discovery validation passed: 133 unique live-stat search titles/descriptions, 34 editorial intent separations, visible factual summaries, and local Web Share/copy fallback.')
