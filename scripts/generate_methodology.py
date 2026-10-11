from pathlib import Path
import json,datetime,html

ROOT=Path('.')
LIVE=ROOT/'data/live-meta.json'
HISTORY=ROOT/'data/meta-history.json'
SCORE=ROOT/'data/meta-score.json'
SCORE_HISTORY=ROOT/'data/meta-score-history.json'
CAT=ROOT/'data/hero-catalog.json'
CORE=ROOT/'data/editorial-core.json'
OUT=ROOT/'methodology.html'
SITEMAP=ROOT/'sitemap.xml'
BASE='https://juanggm04-ship-it.github.io/mlbb-meta-forge/'

for p in [LIVE,HISTORY,SCORE,SCORE_HISTORY,CAT,CORE]:
    if not p.exists():
        raise RuntimeError(f'Methodology dependency missing: {p}')

live=json.loads(LIVE.read_text(encoding='utf-8'))
history=json.loads(HISTORY.read_text(encoding='utf-8'))
score=json.loads(SCORE.read_text(encoding='utf-8'))
score_history=json.loads(SCORE_HISTORY.read_text(encoding='utf-8'))
catalog=json.loads(CAT.read_text(encoding='utf-8'))
core=json.loads(CORE.read_text(encoding='utf-8'))

if live.get('parser_version')!=2 or live.get('rate_unit')!='percentage_points':
    raise RuntimeError('Methodology only supports parser v2 percentage-point data')
if len(live.get('heroes',[]))!=133:
    raise RuntimeError('Methodology expects 133 live heroes')
if len(catalog.get('heroes',[]))!=34 or len(core.get('profiles',{}))!=34:
    raise RuntimeError('Methodology expects 34 editorial heroes/profiles')

snapshots=history.get('snapshots',[])
snapshot_count=len(snapshots)
history_status=score_history.get('history_status')
if snapshot_count<2 and history_status!='waiting_for_real_change':
    raise RuntimeError('Methodology history status mismatch')
if snapshot_count>=2 and history_status!='active':
    raise RuntimeError('Methodology active history status mismatch')

def fmt_dt(value):
    try:
        dt=datetime.datetime.fromisoformat(str(value).replace('Z','+00:00'))
        months=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
        return f'{dt.day} {months[dt.month-1]} {dt.year} · {dt.strftime("%H:%M")} UTC'
    except Exception:
        return html.escape(str(value or '—'))

def esc(value): return html.escape(str(value or '—'))

provider=live.get('provider') or 'Proveedor público'
provider_url=live.get('provider_url') or '#'
source=live.get('source') if isinstance(live.get('source'),dict) else {}
source_name=source.get('name') or 'No especificada'
source_url=source.get('url') or '#'
source_license=source.get('license') or 'No especificada'
measured=fmt_dt(live.get('source_updated'))
fetched=fmt_dt(live.get('fetched_at'))
patch=esc(live.get('patch'))
formula=esc(score.get('formula'))
momentum_formula=esc(score.get('momentum_formula'))
momentum_status=score.get('momentum_status') or 'unknown'
if momentum_status=='neutral_no_history':
    momentum_human='Neutral por falta de un segundo snapshot real. El componente recibe percentil 50 y no se interpreta como tendencia.'
elif momentum_status=='observed':
    momentum_human='Observado para el roster usando el snapshot real anterior.'
else:
    momentum_human='Parcial: solo se usa donde existe comparación histórica válida.'

history_human=(
    f'{snapshot_count} snapshots reales · historial activo.'
    if snapshot_count>=2 else
    '1 snapshot real · esperando un cambio semántico de patch o de WR/ban/pick.'
)

page=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Metodología y fuentes | MLBB Meta Forge</title><meta name="description" content="Cómo Meta Forge obtiene, valida y separa estadísticas live, análisis editorial, historial y Meta Score para MLBB."><link rel="canonical" href="{BASE}methodology.html"><meta name="robots" content="index,follow"><style>
:root{{--bg:#070a12;--card:#0c1422;--line:#263852;--text:#edf5ff;--muted:#8b9bb5;--cyan:#53e6ff;--violet:#b49aff;--gold:#ffd36c;--green:#83e8b7}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 12% 0,#172847 0,transparent 30%),var(--bg);color:var(--text);font-family:system-ui,-apple-system,Segoe UI,sans-serif}}a{{color:var(--cyan);text-decoration:none}}a:hover{{text-decoration:underline}}main{{max-width:980px;margin:auto;padding:28px 18px 80px}}.top{{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}}.brand{{font-weight:950;letter-spacing:.08em}}.hero{{margin-top:26px;padding:30px;border:1px solid #30415f;border-radius:28px;background:linear-gradient(145deg,#0d1728,#17132b)}}.eyebrow{{font-size:10px;font-weight:950;letter-spacing:.15em;color:var(--cyan)}}h1{{font-size:clamp(42px,7vw,72px);line-height:.95;letter-spacing:-.055em;margin:12px 0}}p,li{{color:#9aabc4;line-height:1.65}}.facts{{display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:20px}}.fact{{padding:13px;border:1px solid #273a56;border-radius:14px;background:#09111e}}.fact b{{display:block;font-size:18px}}.fact span{{display:block;margin-top:3px;color:#7486a3;font-size:9px;font-weight:900;letter-spacing:.08em}}section{{margin-top:18px;padding:22px;border:1px solid var(--line);border-radius:20px;background:var(--card)}}section h2{{margin:0 0 9px;font-size:24px;letter-spacing:-.03em}}section h3{{margin:18px 0 7px;font-size:15px}}.split{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.callout{{padding:14px;border:1px solid #344864;border-radius:14px;background:#0a1220}}.callout strong{{color:#dbe8f8}}.good{{border-color:#285443;background:#0b1814}}.warn{{border-color:#5e4b22;background:#18150d}}.formula{{padding:14px;border:1px solid #4d426f;border-radius:14px;background:#151127;color:#cfc0ff;font-weight:850;line-height:1.55}}code{{padding:2px 5px;border-radius:6px;background:#080e18;color:#cae8ff}}table{{width:100%;border-collapse:collapse;margin-top:12px}}th,td{{padding:10px;border-bottom:1px solid #21324a;text-align:left;font-size:12px}}th{{color:#7f91ad;font-size:9px;letter-spacing:.08em}}td{{color:#acbad0}}.status{{display:inline-flex;padding:6px 9px;border:1px solid #4c4124;border-radius:999px;color:var(--gold);font-size:10px;font-weight:900}}footer{{margin-top:24px;color:#6f809c;font-size:11px;line-height:1.6}}@media(max-width:720px){{.facts,.split{{grid-template-columns:1fr 1fr}}}}@media(max-width:500px){{.facts,.split{{grid-template-columns:1fr}}}}
</style></head><body><main><div class="top"><a class="brand" href="./">MLBB FORGE</a><div><a href="roster/">Live Roster</a> · <a href="trends/">Trends</a></div></div><header class="hero"><div class="eyebrow">DATA & EDITORIAL METHODOLOGY</div><h1>Qué sabemos, qué inferimos y qué no fingimos saber.</h1><p>Meta Forge separa las estadísticas públicas del análisis editorial. Esta página documenta el contrato de datos, las transformaciones, el historial y el Meta Score para que las cifras sean auditables y las recomendaciones no se disfracen de datos oficiales.</p><div class="facts"><div class="fact"><b>{len(live['heroes'])}</b><span>HÉROES LIVE</span></div><div class="fact"><b>{len(catalog['heroes'])}</b><span>PERFILES EDITORIALES</span></div><div class="fact"><b>{patch}</b><span>PATCH REPORTADO</span></div><div class="fact"><b>{snapshot_count}</b><span>SNAPSHOT REAL</span></div></div></header>
<section><h2>1. Fuente y frescura</h2><div class="split"><div class="callout"><strong>Proveedor del snapshot</strong><p><a href="{html.escape(provider_url,quote=True)}" rel="noopener noreferrer">{esc(provider)}</a>. Meta Forge lo trata como proveedor público de datos, no como fuente oficial de MOONTON.</p></div><div class="callout"><strong>Fuente declarada por el proveedor</strong><p><a href="{html.escape(source_url,quote=True)}" rel="noopener noreferrer">{esc(source_name)}</a> · licencia reportada: {esc(source_license)}.</p></div></div><table><tr><th>SEÑAL</th><th>VALOR ACTUAL</th></tr><tr><td>Medición informada por la fuente</td><td>{measured}</td></tr><tr><td>Consulta/validación de Meta Forge</td><td>{fetched}</td></tr><tr><td>Criterio de frescura</td><td><code>source_updated</code> cuando existe; <code>fetched_at</code> solo como fallback</td></tr></table><p>“Consultado hoy” no significa “medido hoy”. El panel de salud usa la fecha de medición de la fuente cuando está disponible.</p></section>
<section><h2>2. Contrato live</h2><p>Cada héroe del roster estadístico contiene exactamente cinco campos:</p><div class="formula"><code>key</code> · <code>name</code> · <code>wr</code> · <code>ban</code> · <code>pick</code></div><p>WR, ban rate y pick rate se almacenan en <strong>puntos porcentuales</strong>. Un valor <code>0.65</code> significa <strong>0.65%</strong>, no 65%.</p><div class="callout good"><strong>Frontera intencional:</strong><p>El snapshot live no guarda tier, línea, rol, counters ni sinergias. Esas capas solo aparecen desde el catálogo/core editorial cuando existe cobertura curada.</p></div><h3>Identidad de héroes</h3><p>Para cruzar nombres entre fuentes se usa una llave normalizada: minúsculas, sin tildes ni puntuación y con <code>&amp;</code> tratado como <code>and</code>. Esto permite resolver variantes como “Popol &amp; Kupa” y “Popol and Kupa” sin cambiar el nombre visible.</p></section>
<section><h2>3. Corrección del parser v2</h2><div class="callout warn"><strong>Transparencia de corrección</strong><p>El 11 oct 2026 se corrigió un error anterior: algunas tasas menores o iguales a 1 ya venían expresadas en puntos porcentuales por el proveedor, pero Meta Forge podía multiplicarlas otra vez por 100. Por ejemplo, 0.65% podía representarse erróneamente como 65%.</p><p>La corrección v2 eliminó ese reescalado. Como era una migración técnica y no un cambio real del meta, se descartó cualquier comparación contaminada y el historial se reinició a un único snapshot corregido. No se fabricaron deltas.</p></div></section>
<section><h2>4. Historial semántico</h2><span class="status">{html.escape(history_human)}</span><p>Una nueva consulta del mismo snapshot no crea tendencia. Meta Forge añade un punto histórico solo cuando cambia el patch o cambia de verdad alguna tasa live WR/ban/pick. Fechas de consulta, orden de respuesta, nombres con puntuación distinta o metadata externa no crean un snapshot nuevo.</p><p>Esto evita sparklines y flechas construidas con “cambios” administrativos.</p></section>
<section><h2>5. Meta Score</h2><p>Meta Score es una señal estadística interna en escala 0–100. <strong>No es tier, probabilidad de victoria, counter score ni ranking oficial.</strong></p><div class="formula">{formula}</div><h3>Momentum</h3><div class="formula">{momentum_formula}</div><p>{html.escape(momentum_human)}</p><p>Las métricas se convierten a percentiles relativos dentro del roster live. Los empates reciben percentil promedio, por lo que dos héroes con el mismo valor no se separan artificialmente por orden alfabético.</p></section>
<section><h2>6. Capa editorial</h2><p>Meta Forge mantiene {len(catalog['heroes'])} héroes con cobertura editorial curada. Aquí viven línea, rol, tier editorial, perfiles de draft y relaciones directas <code>good/warn</code>. Estas relaciones describen interacciones de draft y estilo, no tasas verificadas de matchup.</p><p>Hero Compare solo muestra contexto estratégico si existe perfil editorial. Los demás héroes conservan únicamente la comparación estadística live.</p></section>
<section><h2>7. Qué no afirmar</h2><ul><li>El proveedor público no se presenta como API oficial de Mobile Legends.</li><li>El tier editorial no es un tier oficial de MOONTON.</li><li>Meta Score no predice el resultado de una partida.</li><li>Un ban rate o pick rate alto no demuestra por sí solo que un héroe sea más fuerte.</li><li>Con un solo snapshot real no existe tendencia observada. El momentum queda neutral hasta tener comparación válida.</li></ul></section>
<footer>Proyecto fan independiente. Para privacidad y condiciones consulta <a href="privacy.html">Privacidad</a> y <a href="terms.html">Términos</a>. Esta metodología describe el funcionamiento técnico/editorial actual del sitio y puede evolucionar cuando cambien las fuentes o el modelo de datos.</footer></main></body></html>'''

OUT.write_text(page,encoding='utf-8')

if SITEMAP.exists():
    s=SITEMAP.read_text(encoding='utf-8')
    url=BASE+'methodology.html'
    if url not in s:
        s=s.replace('</urlset>',f'<url><loc>{url}</loc></url></urlset>')
        SITEMAP.write_text(s,encoding='utf-8')

print(f'Generated methodology page: live={len(live["heroes"])}; editorial={len(catalog["heroes"])}; snapshots={snapshot_count}; status={history_status}; parser={live.get("parser_version")}; unit={live.get("rate_unit")}')
