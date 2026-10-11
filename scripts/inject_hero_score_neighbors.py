from pathlib import Path
from urllib.parse import quote
import json,re,unicodedata,html

SCORE=Path('data/meta-score.json')
ROOT=Path('stats/heroes')
if not SCORE.exists(): raise RuntimeError('data/meta-score.json is required for hero score neighbors')
rows=json.loads(SCORE.read_text(encoding='utf-8')).get('heroes',[])
if len(rows)!=133: raise RuntimeError(f'Expected 133 score rows, got {len(rows)}')
rows=sorted(rows,key=lambda h:h.get('rank',9999))
if [h.get('rank') for h in rows] != list(range(1,134)): raise RuntimeError('Meta Score ranks must be contiguous before neighbor navigation')

def slug(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')
by_slug={slug(r['name']):(i,r) for i,r in enumerate(rows)}

CSS='''<style id="hero-score-neighbors-style">.hero-neighbors{border:1px solid #2a3d59;background:#0a1220;border-radius:20px;padding:18px;margin-top:14px}.hero-neighbors-head{display:flex;justify-content:space-between;gap:16px;align-items:end;margin-bottom:12px}.hero-neighbors-head h2{margin:4px 0 0;font-size:18px}.hero-neighbors-head span{color:#8b9bb4;font-size:10px;line-height:1.45}.hero-neighbor-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.hero-neighbor-card{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:13px;border:1px solid #283a55;border-radius:14px;background:#0c1625}.hero-neighbor-card small{display:block;color:#7185a2;font-size:9px;font-weight:900;letter-spacing:.08em}.hero-neighbor-card b{display:block;margin-top:4px;color:#e7f0ff;font-size:15px}.hero-neighbor-card strong{color:#c9b6ff;font-size:18px}.hero-neighbor-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}.hero-neighbor-actions a{font-size:9px;font-weight:850;color:#8ddff2;text-decoration:none}.hero-neighbor-empty{padding:13px;border:1px dashed #293a53;border-radius:14px;color:#667a98;font-size:11px;display:flex;align-items:center}.hero-neighbor-note{margin:11px 0 0;color:#6f819d;font-size:9px;line-height:1.5}@media(max-width:640px){.hero-neighbor-grid{grid-template-columns:1fr}.hero-neighbors-head{align-items:flex-start;flex-direction:column}}</style>'''

def card(label,row,current):
    if row is None:
        return '<div class="hero-neighbor-empty">No hay otro héroe en este lado del ranking.</div>'
    name=html.escape(row['name']);s=slug(row['name']);score=float(row['score']);rank=int(row['rank'])
    compare=f'../../../compare/?a={quote(current,safe="")}&b={quote(row["name"],safe="")}'
    return (f'<article class="hero-neighbor-card" data-neighbor-rank="{rank}"><div><small>{label}</small><b>{name} · #{rank}</b>'
            f'<div class="hero-neighbor-actions"><a href="../{s}/">Abrir ficha</a><a href="{compare}">Comparar</a></div></div><strong>{score:.1f}</strong></article>')

pages=sorted(ROOT.glob('*/index.html'))
if len(pages)!=133: raise RuntimeError(f'Expected 133 stat pages, got {len(pages)}')
changed=0
for page in pages:
    text=page.read_text(encoding='utf-8')
    if 'id="heroScoreNeighbors"' in text: continue
    pair=by_slug.get(page.parent.name)
    if not pair: raise RuntimeError(f'No score row for stat page {page}')
    i,current=pair
    higher=rows[i-1] if i>0 else None
    lower=rows[i+1] if i+1<len(rows) else None
    section=(f'<section id="heroScoreNeighbors" class="hero-neighbors" aria-labelledby="heroScoreNeighborsTitle"><div class="hero-neighbors-head"><div><span>EXPLORA EL RANKING</span><h2 id="heroScoreNeighborsTitle">Vecinos de {html.escape(current["name"])} en Meta Score</h2></div><span>Posición actual: #{current["rank"]} de {len(rows)}</span></div><div class="hero-neighbor-grid">{card("INMEDIATAMENTE ARRIBA",higher,current["name"])}{card("INMEDIATAMENTE ABAJO",lower,current["name"])}</div><p class="hero-neighbor-note">La cercanía en Meta Score solo indica posición estadística próxima. No implica mismo rol, estilo de juego, sinergia ni matchup.</p></section>')
    marker='<details id="heroSourceDetails"'
    if marker not in text: raise RuntimeError(f'Hero source details marker missing in {page}')
    text=text.replace(marker,section+marker,1)
    text=text.replace('</head>',CSS+'</head>',1)
    page.write_text(text,encoding='utf-8');changed+=1
if changed not in (0,133): raise RuntimeError(f'Injected neighbors into only {changed}/133 pages')
print(f'Injected Meta Score neighbor navigation into {len(pages)} live hero pages')
