from pathlib import Path
import json

p=Path('index.html')
HISTORY=Path('data/meta-history.json')
html=p.read_text(encoding='utf-8')
if 'id="dataHealth"' in html:
    print('Data health already injected')
    raise SystemExit

history_count=0
if HISTORY.exists():
    try:
        history=json.loads(HISTORY.read_text(encoding='utf-8'))
        history_count=len(history.get('snapshots',[]))
    except Exception:
        history_count=0
history_status='active' if history_count>=2 else 'waiting_for_real_change' if history_count==1 else 'unavailable'
history_text=(f'{history_count} snapshots' if history_count!=1 else '1 snapshot real') if history_count else '—'

css='''<style>
.data-health{margin:18px 0;padding:16px 18px;border:1px solid #263653;border-radius:18px;background:linear-gradient(145deg,#0b1321,#10182a)}
.data-health-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.data-health-head h4{margin:0;font-size:15px}.data-health-status{display:inline-flex;align-items:center;gap:7px;font-size:11px;font-weight:800}.data-health-dot{width:9px;height:9px;border-radius:50%;background:#49d889;box-shadow:0 0 18px #49d88966}.data-health.warn .data-health-dot{background:#ffcc66;box-shadow:0 0 18px #ffcc6666}.data-health.stale .data-health-dot{background:#ff6f7d;box-shadow:0 0 18px #ff6f7d66}.data-health-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:12px}.data-health-cell{padding:10px 11px;border:1px solid #22314b;border-radius:12px;background:#09101c}.data-health-cell b{display:block;font-size:13px}.data-health-cell span{display:block;margin-top:3px;color:#7889a7;font-size:9px;letter-spacing:.06em}.data-health-cell.history-wait b{color:#ffd36c}.data-health-cell.history-active b{color:#83e8b7}.data-health-note{margin:10px 0 0;color:#7f90ad;font-size:11px;line-height:1.5}@media(max-width:880px){.data-health-grid{grid-template-columns:repeat(3,1fr)}}@media(max-width:600px){.data-health-grid{grid-template-columns:1fr 1fr}}
</style>'''
html=html.replace('</head>',css+'</head>')

history_class='history-active' if history_count>=2 else 'history-wait' if history_count==1 else ''
markup=f'''<div id="dataHealth" class="data-health" data-history-status="{history_status}" data-history-snapshots="{history_count}"><div class="data-health-head"><h4>Estado de los datos</h4><div class="data-health-status"><i class="data-health-dot"></i><span id="dataHealthLabel">Comprobando snapshot…</span></div></div><div class="data-health-grid"><div class="data-health-cell"><b id="dhPatch">—</b><span>PATCH</span></div><div class="data-health-cell"><b id="dhHeroes">—</b><span>HÉROES</span></div><div class="data-health-cell"><b id="dhAge">—</b><span>FRESCURA FUENTE</span></div><div class="data-health-cell {history_class}"><b id="dhHistory">{history_text}</b><span>HISTORIAL</span></div><div class="data-health-cell"><b id="dhSource">—</b><span>PROVEEDOR</span></div></div><p id="dataHealthNote" class="data-health-note">El sitio conserva el último snapshot válido si una sincronización externa falla.</p></div>'''
needle='<div id="homeQuickActions" class="quick-actions">'
if needle in html:
    html=html.replace(needle,markup+needle)
else:
    html=html.replace('<main>', '<main>'+markup, 1)

js=r'''<script>
(()=>{
const root=document.getElementById('dataHealth');if(!root)return;
const label=document.getElementById('dataHealthLabel'),patch=document.getElementById('dhPatch'),heroes=document.getElementById('dhHeroes'),age=document.getElementById('dhAge'),source=document.getElementById('dhSource'),note=document.getElementById('dataHealthNote');
function ageText(days){if(days<=0)return 'hoy';if(days===1)return '1 día';return days+' días'}
function daysFrom(ts){const d=ts?new Date(ts):null;return d&&!Number.isNaN(d.getTime())?Math.max(0,Math.floor((Date.now()-d.getTime())/86400000)):null}
function sourceName(meta){if(meta.provider)return meta.provider;if(meta.source&&typeof meta.source==='object'&&meta.source.name)return meta.source.name;if(typeof meta.source==='string')return meta.source;return meta.source_name||'Snapshot validado'}
function historySuffix(){const n=Number(root.dataset.historySnapshots||0);if(n>=2)return ` · ${n} snapshots reales disponibles para tendencia.`;if(n===1)return ' · Solo hay 1 snapshot real; el historial espera un cambio semántico de patch o tasas.';return ' · Historial temporal no disponible.'}
function apply(meta){
  const sourceTs=meta.source_updated||null;
  const fetchTs=meta.fetched_at||meta.generated_at||meta.updated_at||null;
  const basis=meta.freshness_basis||(sourceTs?'source':fetchTs?'fetched':'unknown');
  const ts=basis==='source'?sourceTs:fetchTs;
  const days=daysFrom(ts);
  const count=Array.isArray(meta.heroes)?meta.heroes.length:(meta.hero_count||'—');
  patch.textContent=meta.patch||(typeof DATA!=='undefined'?DATA.patch:'—')||'—';heroes.textContent=count;source.textContent=sourceName(meta);age.textContent=days===null?'—':(basis==='source'?ageText(days):'consultado '+ageText(days));
  root.classList.remove('warn','stale');
  if(basis==='fetched'){
    if(days!==null&&days>14)root.classList.add('stale');else if(days!==null&&days>7)root.classList.add('warn');
    label.textContent=days!==null&&days>14?'Consulta antigua':'Snapshot consultado';
    note.textContent='La fuente no publicó una fecha propia del dato. Mostramos cuándo Meta Forge consultó y validó el snapshot, sin presentarlo como fecha de actualización de la fuente.'+historySuffix();
    return;
  }
  if(days===null){root.classList.add('warn');label.textContent='Fecha no disponible';note.textContent='No pudimos verificar la antigüedad del snapshot, pero el sitio conserva el último conjunto validado.'+historySuffix()}
  else if(days>14){root.classList.add('stale');label.textContent='Snapshot desactualizado';note.textContent='La fecha informada por la fuente tiene más de 14 días. Úsala con cautela hasta la siguiente sincronización válida.'+historySuffix()}
  else if(days>7){root.classList.add('warn');label.textContent='Snapshot envejeciendo';note.textContent='La fecha informada por la fuente tiene más de una semana.'+historySuffix()}
  else{label.textContent='Snapshot saludable';note.textContent='La fuente informó una fecha reciente y el snapshot pasó las validaciones de Meta Forge.'+historySuffix()}
}
fetch('data/live-meta.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('fallback');return r.json()}).then(apply).catch(()=>apply({patch:typeof DATA!=='undefined'?DATA.patch:null,heroes:typeof DATA!=='undefined'?DATA.heroes:[],updated:typeof DATA!=='undefined'?DATA.updated:null,source_name:'Snapshot integrado'}));
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print(f'Injected data health panel with history readiness: snapshots={history_count}; status={history_status}')
