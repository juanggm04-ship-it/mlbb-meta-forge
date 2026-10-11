from pathlib import Path
import json, html, re, unicodedata

SCORE=Path('data/meta-score.json')
HISTORY=Path('data/meta-score-history.json')
ROOT=Path('stats/heroes')

if not SCORE.exists():
    raise RuntimeError('data/meta-score.json is required')
if not ROOT.exists():
    raise RuntimeError('stats/heroes is required')

score=json.loads(SCORE.read_text(encoding='utf-8'))
rows=score.get('heroes',[])
if len(rows)<100:
    raise RuntimeError(f'Expected >=100 Meta Score rows, got {len(rows)}')
momentum_status=score.get('momentum_status','unknown')

def slug(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')

by_slug={slug(r['name']):r for r in rows if r.get('name')}
latest_by={}
prior_by={}
if HISTORY.exists():
    h=json.loads(HISTORY.read_text(encoding='utf-8'))
    snaps=h.get('snapshots',[])
    if snaps:
        latest_by={r['name']:r for r in snaps[-1].get('heroes',[]) if r.get('name')}
    if len(snaps)>=2:
        prior_by={r['name']:r for r in snaps[-2].get('heroes',[]) if r.get('name')}

CSS='''<style id="hero-meta-score-style">.hero-ms{border:1px solid #35496b;background:linear-gradient(145deg,#0b1423,#151329);border-radius:24px;padding:24px;margin-top:18px}.hero-ms-head{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:end}.hero-ms-kicker{display:block;color:#bfa9ff;font-size:10px;font-weight:900;letter-spacing:.13em}.hero-ms h2{margin:5px 0 0}.hero-ms-score{text-align:right}.hero-ms-score strong{display:block;font-size:42px;line-height:1;color:#c9b7ff;letter-spacing:-.04em}.hero-ms-score span{display:block;color:#8292ad;font-size:10px;margin-top:5px}.hero-ms-bars{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}.hero-ms-metric{border:1px solid #263852;border-radius:15px;padding:12px;background:#0a1220}.hero-ms-metric-head{display:flex;justify-content:space-between;gap:8px;align-items:center;font-size:11px}.hero-ms-metric-head b{font-size:11px}.hero-ms-track{height:8px;background:#111d2d;border-radius:999px;overflow:hidden;margin-top:9px}.hero-ms-fill{height:100%;background:linear-gradient(90deg,#50e6ff,#9a6cff);border-radius:999px}.hero-ms-help{margin-top:8px;color:#7587a4;font-size:10px;line-height:1.45}.hero-ms-history{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}.hero-ms-chip{border:1px solid #2d405c;border-radius:999px;padding:7px 10px;color:#aebbd0;font-size:10px}.hero-ms-up{color:#83e8b7}.hero-ms-down{color:#ff9d9d}.hero-ms-neutral{color:#ffd36c}.hero-ms-note{margin-top:15px;padding-top:13px;border-top:1px solid #253750;color:#7c8eaa;font-size:10px;line-height:1.55}@media(max-width:680px){.hero-ms-head{grid-template-columns:1fr}.hero-ms-score{text-align:left}.hero-ms-bars{grid-template-columns:1fr}}</style>'''

def metric(label,value,help_text):
    v=max(0.0,min(100.0,float(value if isinstance(value,(int,float)) else 50.0)))
    return f'''<div class="hero-ms-metric"><div class="hero-ms-metric-head"><b>{html.escape(label)}</b><span>{v:.1f} pct</span></div><div class="hero-ms-track" aria-hidden="true"><div class="hero-ms-fill" style="width:{v:.1f}%"></div></div><div class="hero-ms-help">{html.escape(help_text)}</div></div>'''

count=0
neutral_count=0
for page in ROOT.glob('*/index.html'):
    r=by_slug.get(page.parent.name)
    if not r:
        continue
    text=page.read_text(encoding='utf-8')
    if 'id="heroMetaScore"' in text:
        continue
    name=r['name']
    latest=latest_by.get(name)
    prior=prior_by.get(name)
    history=''
    if latest and prior:
        ds=round(latest['score']-prior['score'],1)
        dr=prior['rank']-latest['rank']
        cls='hero-ms-up' if ds>0 else 'hero-ms-down' if ds<0 else ''
        history=(f'<div class="hero-ms-history"><span class="hero-ms-chip {cls}">Score {ds:+.1f}</span>'
                 f'<span class="hero-ms-chip {"hero-ms-up" if dr>0 else "hero-ms-down" if dr<0 else ""}">Ranking {dr:+d} puestos</span></div>')
    else:
        history='<div class="hero-ms-history"><span class="hero-ms-chip">Historial insuficiente para calcular evolución</span></div>'

    if r.get('momentum_observed'):
        momentum_help=f"Peso 15%. Percentil de la señal compuesta observada; señal bruta {r.get('momentum_raw',0):+.3f}."
        momentum_note='Momentum observado contra el snapshot anterior.'
    else:
        neutral_count+=1
        momentum_help='Peso 15%. Percentil neutral 50 porque todavía no existe una comparación histórica válida para este héroe.'
        momentum_note='Momentum aún no observado; el 50.º percentil es neutral y no significa “sin cambio”.'

    section=f'''<section id="heroMetaScore" class="hero-ms" aria-labelledby="heroMetaScoreTitle"><div class="hero-ms-head"><div><span class="hero-ms-kicker">META SCORE · ESTADÍSTICO</span><h2 id="heroMetaScoreTitle">¿Por qué {html.escape(name)} tiene {r['score']:.1f}?</h2><p>Desglose relativo frente al roster live. Cada barra es un percentil, no el porcentaje bruto de la métrica.</p></div><div class="hero-ms-score"><strong>{r['score']:.1f}</strong><span>#{r['rank']} de {len(rows)} · {html.escape(r.get('label',''))}</span></div></div><div class="hero-ms-bars">{metric('Win rate',r.get('wr_pct'),'Peso 45% del Meta Score. Percentil de WR dentro del roster.')}{metric('Pick rate',r.get('pick_pct'),'Peso 20%. Señal de presencia, no fuerza por sí sola.')}{metric('Ban rate',r.get('ban_pct'),'Peso 20%. Señal de prioridad o rechazo, no fuerza por sí sola.')}{metric('Momentum' if r.get('momentum_observed') else 'Momentum · neutral',r.get('momentum_pct'),momentum_help)}</div>{history}<div class="hero-ms-note"><b>Fórmula:</b> 45% percentil WR + 20% percentil pick + 20% percentil ban + 15% percentil momentum. Momentum = 60% ΔWR + 25% Δpick + 15% Δban. <span class="{'hero-ms-neutral' if not r.get('momentum_observed') else ''}">{html.escape(momentum_note)}</span> El Meta Score no es tier, counter score ni probabilidad de victoria.</div></section>'''
    text=text.replace('</head>',CSS+'</head>',1)
    marker='<section class="panel"><h2>Procedencia</h2>'
    if marker not in text:
        raise RuntimeError(f'Provenance marker missing in {page}')
    text=text.replace(marker,section+marker,1)
    page.write_text(text,encoding='utf-8')
    count+=1

if count!=len(rows):
    raise RuntimeError(f'Injected Hero Meta Score into {count}/{len(rows)} pages')
if momentum_status=='neutral_no_history' and neutral_count!=len(rows):
    raise RuntimeError(f'Meta Score says neutral_no_history but only {neutral_count}/{len(rows)} hero pages are neutral')
print(f'Injected per-hero Meta Score breakdown into {count} live-stat pages; neutral_momentum={neutral_count}/{len(rows)}')
