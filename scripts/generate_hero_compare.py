from pathlib import Path
import json, html, re, unicodedata

LIVE=Path('data/live-meta.json')
SCORE=Path('data/meta-score.json')
HISTORY=Path('data/meta-score-history.json')
COMPARE=Path('compare/index.html')
ROSTER=Path('roster/index.html')
SITEMAP=Path('sitemap.xml')
BASE='https://juanggm04-ship-it.github.io/mlbb-meta-forge/'

if not LIVE.exists() or not SCORE.exists():
    raise RuntimeError('Live meta and Meta Score are required for Hero Compare')

live=json.loads(LIVE.read_text(encoding='utf-8'))
score=json.loads(SCORE.read_text(encoding='utf-8'))
heroes=[h for h in live.get('heroes',[]) if h.get('name')]
score_by={h['name']:h for h in score.get('heroes',[]) if h.get('name')}
if len(heroes)<100 or len(score_by)<100:
    raise RuntimeError('Hero Compare requires full live roster and Meta Score')

def slug(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')

# Attach latest historical delta when available.
hist_by={}
if HISTORY.exists():
    raw=json.loads(HISTORY.read_text(encoding='utf-8'))
    snaps=raw.get('snapshots',[])
    if len(snaps)>=2:
        a={h['name']:h for h in snaps[-1].get('heroes',[]) if h.get('name')}
        b={h['name']:h for h in snaps[-2].get('heroes',[]) if h.get('name')}
        for name,cur in a.items():
            old=b.get(name)
            if old:
                hist_by[name]={'score_delta':round(cur['score']-old['score'],1),'rank_delta':old['rank']-cur['rank']}

rows=[]
for h in heroes:
    s=score_by.get(h['name'],{})
    rows.append({
        'name':h['name'],'slug':slug(h['name']),'wr':h.get('wr'),'ban':h.get('ban'),'pick':h.get('pick'),
        'score':s.get('score'),'rank':s.get('rank'),'momentum':s.get('momentum_raw'),
        'wr_pct':s.get('wr_pct'),'ban_pct':s.get('ban_pct'),'pick_pct':s.get('pick_pct'),'momentum_pct':s.get('momentum_pct'),
        **hist_by.get(h['name'],{})
    })
rows.sort(key=lambda x:x['name'])
DATA=json.dumps(rows,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
opts=''.join(f'<option value="{html.escape(h["name"],quote=True)}">{html.escape(h["name"])}</option>' for h in rows)

COMPARE.parent.mkdir(exist_ok=True)
page=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Comparar héroes MLBB | Meta Forge</title><meta name="description" content="Compara dos héroes del roster live por WR, ban, pick, Meta Score, momentum y ranking."><link rel="canonical" href="{BASE}compare/"><style>
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 12% 0,#172a4b 0,transparent 30%),#070a12;color:#edf5ff;font-family:system-ui}}main{{max-width:1100px;margin:auto;padding:28px 18px 70px}}a{{color:#5ee7ff;text-decoration:none}}.hero,.panel{{border:1px solid #283952;border-radius:24px;background:#0b1321;padding:22px;margin-top:18px}}h1{{font-size:clamp(40px,7vw,72px);letter-spacing:-.055em;margin:10px 0}}p{{color:#92a3bd;line-height:1.6}}.controls{{display:grid;grid-template-columns:1fr auto 1fr auto;gap:10px;align-items:center}}select,button{{background:#0a111e;color:#eef5ff;border:1px solid #2b3f5d;border-radius:13px;padding:12px;font:inherit}}button{{cursor:pointer;font-weight:800}}.vs{{font-weight:950;color:#8d78ff}}.cards{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}}.card{{border:1px solid #243650;border-radius:18px;padding:18px;background:#0c1625}}.card h2{{margin:0 0 4px;font-size:28px}}.sub{{font-size:11px;color:#7f92ae}}.score{{font-size:44px;font-weight:950;color:#c4acff;margin:10px 0}}.metrics{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}.metric{{padding:11px;border-radius:12px;background:#08111d;border:1px solid #1d2c43}}.metric b{{display:block;font-size:17px}}.metric span{{font-size:9px;color:#71849f}}.compare{{margin-top:14px;display:grid;gap:8px}}.row{{display:grid;grid-template-columns:1fr 120px 1fr;gap:10px;align-items:center;padding:10px;border:1px solid #22334d;border-radius:12px}}.row span{{font-size:11px}}.row strong:nth-child(1){{text-align:right}}.label{{text-align:center;color:#8193ad}}.win{{color:#82e8b6}}.muted{{color:#8193ad}}.note{{font-size:10px;color:#72839e;margin-top:12px}}@media(max-width:700px){{.controls{{grid-template-columns:1fr}}.vs{{text-align:center}}.cards{{grid-template-columns:1fr}}.row{{grid-template-columns:1fr 90px 1fr}}}}</style></head><body><main><a href="../roster/">← Live Roster</a><section class="hero"><span class="sub">HERO COMPARE · LIVE STATS</span><h1>Dos héroes. Una mesa.</h1><p>Comparación estadística del snapshot actual. Un valor mayor no implica automáticamente que un héroe sea mejor en una partida concreta.</p><div class="controls"><select id="a" aria-label="Primer héroe">{opts}</select><span class="vs">VS</span><select id="b" aria-label="Segundo héroe">{opts}</select><button id="share" type="button">Copiar enlace</button></div></section><section class="panel"><div id="cards" class="cards"></div><div id="rows" class="compare"></div><div class="note">Meta Score = señal estadística compuesta, no tier ni probabilidad de victoria. Momentum usa cambios de WR, pick y ban.</div></section></main><script>
const HEROES={DATA};const by=new Map(HEROES.map(h=>[h.name,h]));const sa=document.getElementById('a'),sb=document.getElementById('b'),cards=document.getElementById('cards'),rows=document.getElementById('rows');
const params=new URLSearchParams(location.search);if(by.has(params.get('a')))sa.value=params.get('a');if(by.has(params.get('b')))sb.value=params.get('b');if(!params.get('b')&&HEROES.length>1)sb.value=HEROES[1].name;if(sa.value===sb.value&&HEROES.length>1)sb.value=HEROES.find(h=>h.name!==sa.value).name;
const pct=v=>Number.isFinite(v)?v.toFixed(2)+'%':'—',num=v=>Number.isFinite(v)?v.toFixed(1):'—',mom=v=>Number.isFinite(v)?(v>0?'+':'')+v.toFixed(3):'—';
function card(h){{const trend=Number.isFinite(h.score_delta)?`${{h.score_delta>=0?'+':''}}${{h.score_delta.toFixed(1)}} score · ${{h.rank_delta>=0?'+':''}}${{h.rank_delta}} puestos`:'historial insuficiente';return `<article class="card"><h2>${{h.name}}</h2><div class="sub">#${{h.rank??'—'}} Meta Score · ${{trend}}</div><div class="score">${{num(h.score)}}</div><div class="metrics"><div class="metric"><b>${{pct(h.wr)}}</b><span>WIN RATE</span></div><div class="metric"><b>${{pct(h.ban)}}</b><span>BAN</span></div><div class="metric"><b>${{pct(h.pick)}}</b><span>PICK</span></div></div><p><a href="../stats/heroes/${{h.slug}}/">Abrir ficha →</a></p></article>`}}
function metric(label,key,format,lowerBetter=false){{const a=by.get(sa.value),b=by.get(sb.value),av=a[key],bv=b[key];let ac='',bc='';if(Number.isFinite(av)&&Number.isFinite(bv)&&av!==bv){{const aw=lowerBetter?av<bv:av>bv;ac=aw?'win':'';bc=!aw?'win':''}}return `<div class="row"><strong class="${{ac}}">${{format(av)}}</strong><span class="label">${{label}}</span><strong class="${{bc}}">${{format(bv)}}</strong></div>`}}
function render(){{const a=by.get(sa.value),b=by.get(sb.value);if(!a||!b)return;cards.innerHTML=card(a)+card(b);rows.innerHTML=metric('WR','wr',pct)+metric('Ban','ban',pct)+metric('Pick','pick',pct)+metric('Meta Score','score',num)+metric('Momentum','momentum',mom)+metric('Ranking','rank',v=>Number.isFinite(v)?'#'+v:'—',true);const u=new URL(location.href);u.searchParams.set('a',a.name);u.searchParams.set('b',b.name);history.replaceState(null,'',u)}}
sa.onchange=render;sb.onchange=render;document.getElementById('share').onclick=async()=>{{const u=location.href;try{{await navigator.clipboard.writeText(u);event.currentTarget.textContent='Enlace copiado'}}catch{{prompt('Copia este enlace:',u)}}};render();
</script></body></html>'''
COMPARE.write_text(page,encoding='utf-8')

# Add compare CTA to every live-stat page.
count=0
for p in Path('stats/heroes').glob('*/index.html'):
    text=p.read_text(encoding='utf-8')
    if 'data-hero-compare' in text: continue
    m=re.search(r'<h1>(.*?)</h1>',text,re.S)
    if not m: continue
    name=re.sub(r'<[^>]+>','',m.group(1)).replace('&amp;','&')
    link=f'<a class="btn alt" data-hero-compare href="../../../compare/?a={html.escape(name,quote=True)}">Comparar este héroe →</a>'
    marker='<div class="actions">'
    if marker in text:
        text=text.replace(marker,marker+link,1)
        p.write_text(text,encoding='utf-8');count+=1

# Add compare entry to roster.
if ROSTER.exists():
    text=ROSTER.read_text(encoding='utf-8')
    if 'href="../compare/"' not in text:
        marker='<div class="toolbar">'
        cta='<p><a href="../compare/" style="display:inline-flex;padding:10px 13px;border:1px solid #315173;border-radius:12px;color:#66e8ff">⚔ Comparar 2 héroes</a></p>'
        text=text.replace(marker,cta+marker,1)
        ROSTER.write_text(text,encoding='utf-8')

if SITEMAP.exists():
    text=SITEMAP.read_text(encoding='utf-8');url=BASE+'compare/'
    if url not in text:text=text.replace('</urlset>',f'<url><loc>{url}</loc></url></urlset>')
    SITEMAP.write_text(text,encoding='utf-8')

print(f'Generated Hero Compare for {len(rows)} heroes; compare CTAs added to {count} stat pages')
