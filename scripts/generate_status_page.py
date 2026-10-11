from pathlib import Path
import datetime, html, json, os, subprocess

ROOT=Path('.')
LIVE=ROOT/'data/live-meta.json'
CATALOG=ROOT/'data/hero-catalog.json'
HISTORY=ROOT/'data/meta-history.json'
SCORE=ROOT/'data/meta-score.json'
RELEASE=ROOT/'data/product-release.json'
OUT=ROOT/'data/build-info.json'
PAGE=ROOT/'status/index.html'
SITEMAP=ROOT/'sitemap.xml'
BASE='https://juanggm04-ship-it.github.io/mlbb-meta-forge/'

for p in (LIVE,CATALOG,HISTORY,SCORE,RELEASE):
    if not p.exists(): raise RuntimeError(f'Status dependency missing: {p}')
live=json.loads(LIVE.read_text(encoding='utf-8'))
catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
history=json.loads(HISTORY.read_text(encoding='utf-8'))
score=json.loads(SCORE.read_text(encoding='utf-8'))
release=json.loads(RELEASE.read_text(encoding='utf-8'))
if release.get('schema_version')!=1 or not release.get('release_id') or not release.get('title'):
    raise RuntimeError('Invalid product-release.json contract')
highlights=release.get('highlights',[])
if not isinstance(highlights,list) or not highlights:
    raise RuntimeError('Product release must include at least one highlight')
live_count=len([h for h in live.get('heroes',[]) if h.get('name')])
editorial_count=len([h for h in catalog.get('heroes',[]) if h.get('name')])
snapshots=history.get('snapshots',[]) if isinstance(history,dict) else []
history_points=len(snapshots) if isinstance(snapshots,list) else 0
score_rows=score.get('heroes',[]) if isinstance(score,dict) else []
momentum_observed=sum(1 for h in score_rows if h.get('momentum_observed') is True)
try:
    build_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
except Exception:
    build_sha=os.getenv('GITHUB_SHA') or 'unknown'
generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
history_ready=history_points>=2 and momentum_observed>0
product_release={
    'release_id':release.get('release_id'),
    'title':release.get('title'),
    'published':release.get('published'),
    'highlights':highlights,
}
info={
    'schema_version':1,
    'build_sha':build_sha,
    'build_short':build_sha[:12],
    'generated_at':generated_at,
    'site_url':BASE,
    'product_release':product_release,
    'live_heroes':live_count,
    'editorial_heroes':editorial_count,
    'patch':live.get('patch'),
    'provider':live.get('provider'),
    'source_updated':live.get('source_updated'),
    'fetched_at':live.get('fetched_at'),
    'freshness_basis':live.get('freshness_basis'),
    'parser_version':live.get('parser_version'),
    'rate_unit':live.get('rate_unit'),
    'history_points':history_points,
    'history_ready':history_ready,
    'momentum_observed_heroes':momentum_observed,
    'history_status':'active' if history_ready else 'waiting_for_real_change' if history_points else 'unavailable'
}
OUT.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')

def e(v): return html.escape(str(v if v is not None else '—'))
def date_text(v):
    if not v:return 'No informada'
    return e(v)
status_label='Historial activo' if history_ready else 'Esperando un cambio real' if history_points else 'Historial no disponible'
status_class='ok' if history_ready else 'wait'
release_items=''.join(f'<li>{e(x)}</li>' for x in highlights[:5])
PAGE.parent.mkdir(parents=True,exist_ok=True)
page=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Estado de Meta Forge</title><meta name="description" content="Estado técnico, cobertura, build y frescura de los datos publicados por MLBB Meta Forge."><style>*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 12% 0,#162948 0,transparent 30%),#070a12;color:#edf5ff;font-family:system-ui,-apple-system,Segoe UI,sans-serif}}a{{color:#62e5ff;text-decoration:none}}main{{max-width:980px;margin:auto;padding:30px 18px 70px}}.top{{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}}.hero,.panel{{margin-top:18px;border:1px solid #293b56;border-radius:24px;background:#0b1422;padding:22px}}.eyebrow{{color:#5fe6ff;font-size:10px;font-weight:900;letter-spacing:.14em}}h1{{font-size:clamp(38px,7vw,66px);letter-spacing:-.055em;margin:8px 0}}p,li{{color:#91a2bd;line-height:1.65}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:15px}}.cell{{padding:13px;border:1px solid #253750;border-radius:14px;background:#09121f}}.cell b{{display:block;font-size:16px;overflow-wrap:anywhere}}.cell span{{display:block;margin-top:4px;color:#7486a1;font-size:9px;letter-spacing:.08em}}.badge{{display:inline-flex;padding:7px 10px;border:1px solid #466654;border-radius:999px;color:#83e8b7;background:#0c1b17;font-size:10px;font-weight:900}}.badge.wait{{border-color:#6d5833;color:#ffd278;background:#1b160d}}.timeline{{display:grid;gap:8px;margin-top:13px}}.time{{padding:12px;border-left:3px solid #344c6d;background:#09121f;border-radius:0 12px 12px 0}}.time b{{display:block;font-size:12px}}.time span{{display:block;margin-top:4px;color:#7f91ac;font-size:10px;overflow-wrap:anywhere}}code{{color:#c6b5ff}}.machine-links{{display:flex;gap:12px;flex-wrap:wrap}}@media(max-width:700px){{.grid{{grid-template-columns:1fr 1fr}}}}@media(max-width:480px){{.grid{{grid-template-columns:1fr}}}}</style></head><body><main><div class="top"><a href="../">← Meta Forge</a><a href="../methodology.html">Metodología</a></div><section class="hero"><div class="eyebrow">BUILD + DATA STATUS</div><h1>Estado de Meta Forge.</h1><p>Esta página separa la versión del producto, la versión técnica del sitio y la antigüedad del dato. Una consulta reciente no significa que la fuente haya publicado una medición nueva.</p><span class="badge {status_class}">{e(status_label)}</span><div class="grid"><div class="cell"><b>{e(live_count)}</b><span>HÉROES LIVE</span></div><div class="cell"><b>{e(editorial_count)}</b><span>PERFILES EDITORIALES</span></div><div class="cell"><b>{e(live.get('patch'))}</b><span>PATCH DETECTADO</span></div><div class="cell"><b>{e(history_points)}</b><span>SNAPSHOTS SEMÁNTICOS</span></div><div class="cell"><b>{e(momentum_observed)}</b><span>MOMENTUM OBSERVADO</span></div><div class="cell"><b>{e(release.get('release_id'))}</b><span>RELEASE DE PRODUCTO</span></div></div></section><section class="panel"><div class="eyebrow">PRODUCT RELEASE</div><h2>{e(release.get('title'))}</h2><p>Release estable: <b>{e(release.get('release_id'))}</b> · publicada: <b>{e(release.get('published'))}</b>. Este identificador cambia cuando lanzamos funciones de producto, no por una simple consulta diaria de datos.</p><ul>{release_items}</ul></section><section class="panel"><div class="eyebrow">TRES RELOJES DE DATOS Y BUILD</div><h2>Frescura sin maquillaje</h2><div class="timeline"><div class="time"><b>1 · Medición informada por la fuente</b><span>{date_text(live.get('source_updated'))}</span></div><div class="time"><b>2 · Última consulta validada por Meta Forge</b><span>{date_text(live.get('fetched_at'))}</span></div><div class="time"><b>3 · Build publicado</b><span>{date_text(generated_at)}</span></div></div><p>Proveedor del snapshot: <b>{e(live.get('provider'))}</b>. Base de frescura: <b>{e(live.get('freshness_basis'))}</b>. Si la fuente no cambia WR, ban, pick o patch, no se inventa un nuevo punto histórico.</p></section><section class="panel"><div class="eyebrow">BUILD</div><h2>Versión reproducible</h2><p>Commit: <code>{e(build_sha)}</code></p><p>Parser: <b>v{e(live.get('parser_version'))}</b> · catálogo editorial: <b>{e(editorial_count)}</b> perfiles · cobertura live: <b>{e(live_count)}</b> héroes.</p><p class="machine-links"><a href="../data/build-info.json">Abrir build-info.json →</a><a href="../data/integrity.json">Ver SHA-256 del artefacto →</a><a href="../data/product-release.json">Ver product-release.json →</a></p></section></main></body></html>'''
PAGE.write_text(page,encoding='utf-8')
if SITEMAP.exists():
    text=SITEMAP.read_text(encoding='utf-8');url=BASE+'status/'
    if url not in text:text=text.replace('</urlset>',f'<url><loc>{url}</loc></url></urlset>')
    SITEMAP.write_text(text,encoding='utf-8')
print(f'Status page generated: build={build_sha[:12]}; release={release.get("release_id")}; live={live_count}; editorial={editorial_count}; history={history_points}; momentum_observed={momentum_observed}; history_ready={history_ready}; integrity_link=true')
