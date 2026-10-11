from pathlib import Path
import json,datetime

TARGETS=[Path('index.html'),Path('trends/index.html'),Path('my-meta/index.html'),Path('roster/index.html')]
TARGETS += sorted(Path('heroes').glob('*/index.html')) if Path('heroes').exists() else []
TARGETS += sorted(Path('stats/heroes').glob('*/index.html')) if Path('stats/heroes').exists() else []

LIVE=Path('data/live-meta.json')
METHOD=Path('methodology.html')
if not LIVE.exists():
    raise RuntimeError('data/live-meta.json is required for provenance')
if not METHOD.exists():
    raise RuntimeError('methodology.html must be generated before provenance')
live=json.loads(LIVE.read_text(encoding='utf-8'))
if live.get('parser_version')!=2 or live.get('rate_unit')!='percentage_points':
    raise RuntimeError('Provenance requires parser v2 percentage-point live data')
source_updated=live.get('source_updated')
fetched_at=live.get('fetched_at')
if not source_updated or not fetched_at:
    raise RuntimeError('Provenance requires source_updated and fetched_at')

def pretty_date(value):
    try:
        dt=datetime.datetime.fromisoformat(str(value).replace('Z','+00:00'))
        months=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
        return f'{dt.day} {months[dt.month-1]} {dt.year}'
    except Exception:
        return str(value)[:10]

measured=pretty_date(source_updated)
fetched=pretty_date(fetched_at)
patch=live.get('patch') or 'sin dato'

CSS='''<style id="data-provenance-style">
.data-provenance{max-width:1180px;margin:18px auto;padding:0 18px;box-sizing:border-box}.data-provenance-inner{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;padding:11px 13px;border:1px solid #263653;border-radius:14px;background:#09111dcc;color:#8798b5;font-size:11px;line-height:1.45}.data-provenance-tags{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.data-prov-tag{display:inline-flex;align-items:center;gap:6px;padding:5px 8px;border:1px solid #2a3b57;border-radius:999px;background:#0c1625;color:#b9c7dc;font-weight:800;letter-spacing:.04em}.data-prov-tag i{width:7px;height:7px;border-radius:50%;display:inline-block}.data-prov-live i{background:#45d99a;box-shadow:0 0 12px #45d99a66}.data-prov-editorial i{background:#b78cff;box-shadow:0 0 12px #b78cff55}.data-prov-contract i{background:#ffd36c;box-shadow:0 0 12px #ffd36c55}.data-provenance details{max-width:690px}.data-provenance summary{cursor:pointer;color:#9fb0c9;font-weight:700;list-style:none}.data-provenance summary::-webkit-details-marker{display:none}.data-provenance details[open] summary{margin-bottom:6px}.data-provenance p{margin:0;color:#788aa8}.data-provenance p+p{margin-top:5px}.data-provenance strong{color:#b9c7dc}.data-provenance a{color:#8ad8ff;text-decoration:none;font-weight:800}.data-provenance a:hover{text-decoration:underline}@media(max-width:700px){.data-provenance{padding:0 12px}.data-provenance-inner{align-items:flex-start}.data-provenance details{width:100%}}
</style>'''

MARKUP=f'''<aside id="dataProvenance" class="data-provenance" aria-label="Procedencia de los datos"><div class="data-provenance-inner"><div class="data-provenance-tags"><span class="data-prov-tag data-prov-live"><i aria-hidden="true"></i>LIVE STATS · WR / BAN / PICK</span><span class="data-prov-tag data-prov-editorial"><i aria-hidden="true"></i>EDITORIAL · TIER / DRAFT / SINERGIAS</span><span class="data-prov-tag data-prov-contract"><i aria-hidden="true"></i>DATA CONTRACT · % POINTS</span></div><details><summary>¿Qué significa esto?</summary><p>WR, ban rate y pick rate vienen del snapshot público validado y se expresan en <strong>puntos porcentuales</strong>. Medición del proveedor: <strong>{measured}</strong> · consulta de Meta Forge: <strong>{fetched}</strong> · patch <strong>{patch}</strong>.</p><p>Los tiers, recomendaciones, perfiles, sinergias y análisis de draft solo aparecen donde Meta Forge tiene una capa editorial curada; no representan datos oficiales ni una probabilidad de victoria.</p><p><a href="/mlbb-meta-forge/methodology.html" data-methodology-link>Metodología completa →</a></p></details></div></aside>'''

changed=0
for path in TARGETS:
    if not path.exists():
        continue
    html=path.read_text(encoding='utf-8')
    if 'id="dataProvenance"' in html:
        continue
    if '</head>' in html:
        html=html.replace('</head>',CSS+'</head>',1)
    if '</main>' in html:
        html=html.replace('</main>',MARKUP+'</main>',1)
    else:
        html=html.replace('</body>',MARKUP+'</body>',1)
    path.write_text(html,encoding='utf-8')
    changed+=1

expected_min=130 if LIVE.exists() else 30
if changed < expected_min:
    raise RuntimeError(f'Data provenance injected into only {changed} pages; expected at least {expected_min}')
print(f'Injected data provenance into {changed} pages; methodology linked; rate_unit=percentage_points; source_measured={source_updated}; fetched_at={fetched_at}')
