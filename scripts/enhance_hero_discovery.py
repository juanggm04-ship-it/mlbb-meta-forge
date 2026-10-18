from pathlib import Path
import json, re, html
from hero_identity import hero_key

LIVE=Path('data/live-meta.json')
SCORE=Path('data/meta-score.json')
ROOT=Path('stats/heroes')
for p in (LIVE,SCORE):
    if not p.exists(): raise RuntimeError(f'Missing hero discovery dependency: {p}')
if not ROOT.exists(): raise RuntimeError('stats/heroes is required')

live=json.loads(LIVE.read_text(encoding='utf-8'))
score=json.loads(SCORE.read_text(encoding='utf-8'))
heroes=live.get('heroes',[]); scores=score.get('heroes',[])
if len(heroes)!=133 or len(scores)!=133:
    raise RuntimeError(f'Hero discovery requires 133 live/score rows; got live={len(heroes)} score={len(scores)}')
live_by={hero_key(h['name']):h for h in heroes if h.get('name')}
score_by={hero_key(h['name']):h for h in scores if h.get('name')}
patch=str(live.get('patch') or 'actual')
updated=str(live.get('updated') or live.get('source_updated') or '').split('T')[0] or 'reciente'

CSS='''<style id="hero-discovery-style">.hero-search-summary{margin-top:18px;padding:18px;border:1px solid #2a3d59;border-radius:18px;background:linear-gradient(145deg,#0a1320,#0d1727)}.hero-search-summary h2{margin:0 0 8px;font-size:18px}.hero-search-summary p{margin:0;color:#93a5bf;font-size:12px;line-height:1.65}.hero-search-summary a{color:#64e5ff}.hero-share-status{display:block;min-height:16px;margin-top:8px;color:#7f93af;font-size:10px}.hero-share-status.ok{color:#79e8c4}.hero-share-status.warn{color:#ffd17a}</style>'''
JS='''<script id="hero-discovery-script">(()=>{const b=document.getElementById('heroShareButton'),s=document.getElementById('heroShareStatus');if(!b||!s)return;const text=b.dataset.shareText||document.title;function set(m,k=''){s.textContent=m;s.className='hero-share-status'+(k?' '+k:'')}async function copy(v){if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(v);return}const t=document.createElement('textarea');t.value=v;t.setAttribute('readonly','');t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.select();document.execCommand('copy');t.remove()}b.addEventListener('click',async()=>{try{if(navigator.share){await navigator.share({title:document.title,text,url:location.href});set('Ficha compartida.','ok')}else{await copy(text+' '+location.href);set('Resumen y enlace copiados.','ok')}}catch(e){if(e&&e.name==='AbortError')return;try{await copy(location.href);set('Enlace copiado.','ok')}catch{set('No se pudo compartir automáticamente.','warn')}}})})();</script>'''

def pct(v):
    return f'{float(v):.2f}%'

pages=sorted(ROOT.glob('*/index.html'))
if len(pages)!=133: raise RuntimeError(f'Expected 133 live hero pages, found {len(pages)}')
changed=0; titles=[]
for page in pages:
    text=page.read_text(encoding='utf-8')
    if 'id="heroSearchSummary"' in text:
        continue
    m=re.search(r'<h1>(.*?)</h1>',text,re.S|re.I)
    if not m: raise RuntimeError(f'Hero heading missing in {page}')
    name=html.unescape(re.sub(r'<[^>]+>','',m.group(1))).strip(); key=hero_key(name)
    row=live_by.get(key); sr=score_by.get(key)
    if not row or not sr: raise RuntimeError(f'Could not resolve discovery data for {name}')
    wr=pct(row['wr']); ban=pct(row['ban']); pick=pct(row['pick']); ms=float(sr['score']); rank=int(sr['rank'])
    title=f'{name} MLBB Win Rate {wr} · Ban {ban} | Meta Forge'
    desc=f'{name} en MLBB patch {patch}: win rate {wr}, ban rate {ban}, pick rate {pick} y Meta Score {ms:.1f} (#{rank}/133). Datos live actualizados {updated}.'
    if len(title)>78: raise RuntimeError(f'Hero discovery title too long ({len(title)}): {name}')
    if len(desc)>190: raise RuntimeError(f'Hero discovery description too long ({len(desc)}): {name}')
    text,n_title=re.subn(r'<title>.*?</title>',f'<title>{html.escape(title)}</title>',text,count=1,flags=re.S|re.I)
    if n_title!=1: raise RuntimeError(f'Expected one title in {page}')
    escaped_desc=html.escape(desc,quote=True)
    text,n_desc=re.subn(r'<meta\s+name=["\']description["\']\s+content=["\'].*?["\']\s*/?>',f'<meta name="description" content="{escaped_desc}">',text,count=1,flags=re.S|re.I)
    if n_desc!=1: raise RuntimeError(f'Expected one description in {page}')
    share_text=f'{name} MLBB · WR {wr} · Ban {ban} · Pick {pick} · Meta Score {ms:.1f} (#{rank}/133)'
    button=f'<button id="heroShareButton" type="button" data-share-text="{html.escape(share_text,quote=True)}">↗ Compartir</button>'
    nav_end=text.find('</nav>',text.find('id="heroQuickActions"'))
    if nav_end<0: raise RuntimeError(f'Hero quick actions missing in {page}')
    text=text[:nav_end]+button+text[nav_end:]
    status='<span id="heroShareStatus" class="hero-share-status" aria-live="polite"></span>'
    nav_close=text.find('</nav>',text.find('id="heroQuickActions"'))+6
    text=text[:nav_close]+status+text[nav_close:]
    summary=(f'<section id="heroSearchSummary" class="hero-search-summary" aria-labelledby="heroSearchSummaryTitle"><h2 id="heroSearchSummaryTitle">{html.escape(name)} en el meta actual</h2><p>En el snapshot live del patch <strong>{html.escape(patch)}</strong>, {html.escape(name)} registra <strong>{wr} de win rate</strong>, <strong>{ban} de ban rate</strong> y <strong>{pick} de pick rate</strong>. Su Meta Score estadístico es <strong>{ms:.1f}</strong>, posición <strong>#{rank} de 133</strong>. El Meta Score no es un tier ni una probabilidad de victoria. <a href="../../../methodology.html">Ver metodología</a>.</p></section>')
    source_marker='<details id="heroSourceDetails"'
    source_pos=text.find(source_marker)
    if source_pos<0: raise RuntimeError(f'Hero source details missing in {page}')
    text=text[:source_pos]+summary+text[source_pos:]
    text=text.replace('</head>',CSS+'</head>',1).replace('</body>',JS+'</body>',1)
    page.write_text(text,encoding='utf-8');changed+=1;titles.append(title)
if changed not in (0,len(pages)): raise RuntimeError(f'Enhanced only {changed}/{len(pages)} hero discovery pages')
if changed and len(set(titles))!=len(titles): raise RuntimeError('Hero discovery titles must be unique')
print(f'Hero discovery enhanced: pages={len(pages)}; unique_titles=133; search_intent=live-stats; share=web-share-with-copy-fallback; patch={patch}; updated={updated}')
