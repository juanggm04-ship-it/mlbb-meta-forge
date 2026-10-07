from pathlib import Path

TARGETS=[Path('index.html'),Path('trends/index.html'),Path('my-meta/index.html')]
TARGETS += sorted(Path('heroes').glob('*/index.html')) if Path('heroes').exists() else []

CSS='''<style id="data-provenance-style">
.data-provenance{max-width:1180px;margin:18px auto;padding:0 18px;box-sizing:border-box}.data-provenance-inner{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;padding:11px 13px;border:1px solid #263653;border-radius:14px;background:#09111dcc;color:#8798b5;font-size:11px;line-height:1.45}.data-provenance-tags{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.data-prov-tag{display:inline-flex;align-items:center;gap:6px;padding:5px 8px;border:1px solid #2a3b57;border-radius:999px;background:#0c1625;color:#b9c7dc;font-weight:800;letter-spacing:.04em}.data-prov-tag i{width:7px;height:7px;border-radius:50%;display:inline-block}.data-prov-live i{background:#45d99a;box-shadow:0 0 12px #45d99a66}.data-prov-editorial i{background:#b78cff;box-shadow:0 0 12px #b78cff55}.data-provenance details{max-width:620px}.data-provenance summary{cursor:pointer;color:#9fb0c9;font-weight:700;list-style:none}.data-provenance summary::-webkit-details-marker{display:none}.data-provenance details[open] summary{margin-bottom:6px}.data-provenance p{margin:0;color:#788aa8}.data-provenance a{color:#8ad8ff;text-decoration:none}.data-provenance a:hover{text-decoration:underline}@media(max-width:700px){.data-provenance{padding:0 12px}.data-provenance-inner{align-items:flex-start}.data-provenance details{width:100%}}
</style>'''

MARKUP='''<aside id="dataProvenance" class="data-provenance" aria-label="Procedencia de los datos"><div class="data-provenance-inner"><div class="data-provenance-tags"><span class="data-prov-tag data-prov-live"><i aria-hidden="true"></i>LIVE STATS · WR / BAN / PICK</span><span class="data-prov-tag data-prov-editorial"><i aria-hidden="true"></i>EDITORIAL · TIER / DRAFT / SINERGIAS</span></div><details><summary>¿Qué significa esto?</summary><p>WR, ban rate y pick rate se sincronizan desde el snapshot público validado. Los tiers, recomendaciones, perfiles, sinergias y análisis de draft son criterios editoriales de Meta Forge y no representan datos oficiales ni una probabilidad de victoria.</p></details></div></aside>'''

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

if changed < 30:
    raise RuntimeError(f'Data provenance injected into only {changed} pages; expected at least 30')
print(f'Injected data provenance into {changed} pages')
