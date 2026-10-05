from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'id="dataHealth"' in html:
    print('Data health already injected')
    raise SystemExit

css='''<style>
.data-health{margin:18px 0;padding:16px 18px;border:1px solid #263653;border-radius:18px;background:linear-gradient(145deg,#0b1321,#10182a)}
.data-health-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.data-health-head h4{margin:0;font-size:15px}.data-health-status{display:inline-flex;align-items:center;gap:7px;font-size:11px;font-weight:800}.data-health-dot{width:9px;height:9px;border-radius:50%;background:#49d889;box-shadow:0 0 18px #49d88966}.data-health.warn .data-health-dot{background:#ffcc66;box-shadow:0 0 18px #ffcc6666}.data-health.stale .data-health-dot{background:#ff6f7d;box-shadow:0 0 18px #ff6f7d66}.data-health-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px}.data-health-cell{padding:10px 11px;border:1px solid #22314b;border-radius:12px;background:#09101c}.data-health-cell b{display:block;font-size:13px}.data-health-cell span{display:block;margin-top:3px;color:#7889a7;font-size:9px;letter-spacing:.06em}.data-health-note{margin:10px 0 0;color:#7f90ad;font-size:11px;line-height:1.5}@media(max-width:760px){.data-health-grid{grid-template-columns:1fr 1fr}}
</style>'''
html=html.replace('</head>',css+'</head>')

markup='''<div id="dataHealth" class="data-health"><div class="data-health-head"><h4>Estado de los datos</h4><div class="data-health-status"><i class="data-health-dot"></i><span id="dataHealthLabel">Comprobando snapshot…</span></div></div><div class="data-health-grid"><div class="data-health-cell"><b id="dhPatch">—</b><span>PATCH</span></div><div class="data-health-cell"><b id="dhHeroes">—</b><span>HÉROES</span></div><div class="data-health-cell"><b id="dhAge">—</b><span>ANTIGÜEDAD</span></div><div class="data-health-cell"><b id="dhSource">—</b><span>FUENTE</span></div></div><p id="dataHealthNote" class="data-health-note">El sitio conserva el último snapshot válido si una sincronización externa falla.</p></div>'''
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
function apply(meta){
  const ts=meta.generated_at||meta.updated_at||meta.updated||meta.timestamp;
  const d=ts?new Date(ts):null;
  const validDate=d&&!Number.isNaN(d.getTime());
  const days=validDate?Math.max(0,Math.floor((Date.now()-d.getTime())/86400000)):null;
  const count=Array.isArray(meta.heroes)?meta.heroes.length:(meta.hero_count||'—');
  patch.textContent=meta.patch||DATA?.patch||'—';heroes.textContent=count;source.textContent=(meta.source_name||meta.source||'Snapshot validado').toString().replace(/^https?:\/\//,'').split('/')[0];age.textContent=days===null?'—':ageText(days);
  root.classList.remove('warn','stale');
  if(days===null){root.classList.add('warn');label.textContent='Fecha no disponible';note.textContent='No pudimos verificar la antigüedad del snapshot, pero el sitio conserva el último conjunto validado.'}
  else if(days>14){root.classList.add('stale');label.textContent='Snapshot desactualizado';note.textContent='Los datos tienen más de 14 días. Úsalos con cautela hasta la siguiente sincronización válida.'}
  else if(days>7){root.classList.add('warn');label.textContent='Snapshot envejeciendo';note.textContent='Los datos tienen más de una semana. La próxima sincronización debería refrescarlos pronto.'}
  else{label.textContent='Snapshot saludable';note.textContent='Datos sincronizados y validados. Si la fuente externa falla, se conserva automáticamente el último snapshot válido.'}
}
fetch('data/live-meta.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('fallback');return r.json()}).then(apply).catch(()=>apply({patch:DATA?.patch,heroes:DATA?.heroes||[],updated:DATA?.updated,source_name:'Snapshot integrado'}));
})();
</script>'''
html=html.replace('</body>',js+'</body>')
p.write_text(html,encoding='utf-8')
print('Injected data health panel')
