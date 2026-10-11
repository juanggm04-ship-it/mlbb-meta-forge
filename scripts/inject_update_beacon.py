from pathlib import Path

TARGETS={
    Path('index.html'):'./',
    Path('roster/index.html'):'../',
    Path('trends/index.html'):'../',
    Path('compare/index.html'):'../',
    Path('my-meta/index.html'):'../',
}
STYLE='''<style id="mf-update-beacon-style">#mfUpdateBeacon{position:fixed;z-index:99997;top:14px;right:14px;width:min(390px,calc(100vw - 28px));padding:14px;border:1px solid #35506f;border-radius:18px;background:linear-gradient(145deg,#0b1726,#0a111d);color:#eef7ff;box-shadow:0 18px 55px #000a;font-family:system-ui,-apple-system,Segoe UI,sans-serif}#mfUpdateBeacon[hidden]{display:none!important}#mfUpdateBeacon .ub-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}#mfUpdateBeacon .ub-kicker{font-size:9px;font-weight:950;letter-spacing:.14em;color:#58e4ff}#mfUpdateBeacon strong{display:block;margin-top:4px;font-size:15px}#mfUpdateBeacon p{margin:7px 0 0;color:#96a9c3;font-size:12px;line-height:1.5}#mfUpdateBeacon .ub-close{border:1px solid #33465f;background:#0b1421;color:#a9bdd5;border-radius:10px;min-width:32px;height:32px;cursor:pointer}#mfUpdateBeacon .ub-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:11px}#mfUpdateBeacon .ub-action{display:inline-flex;padding:8px 10px;border:1px solid #35506f;border-radius:10px;color:#b8cae2;text-decoration:none;font-size:10px;font-weight:900}#mfUpdateBeacon .ub-action.primary{background:#4ce5ff;color:#06111c;border-color:#4ce5ff}@media(max-width:620px){#mfUpdateBeacon{top:auto;right:14px;bottom:74px}}</style>'''
MARKUP='''<aside id="mfUpdateBeacon" hidden aria-live="polite" aria-label="Novedades desde tu última visita"><div class="ub-top"><div><div class="ub-kicker">DESDE TU ÚLTIMA VISITA</div><strong id="mfUpdateTitle">Hay novedades</strong><p id="mfUpdateText"></p></div><button class="ub-close" id="mfUpdateDismiss" type="button" aria-label="Marcar novedades como vistas">×</button></div><div class="ub-actions"><a class="ub-action primary" id="mfUpdateDataLink" href="#" hidden>Ver Trends</a><a class="ub-action" id="mfUpdateProductLink" href="#" hidden>Ver versión</a></div></aside>'''

RUNTIME_TMPL='''<script id="mf-update-beacon-runtime">(()=>{{
const PREFIX={prefix!r},KEY='mf_seen_updates_v1';
const box=document.getElementById('mfUpdateBeacon'),title=document.getElementById('mfUpdateTitle'),text=document.getElementById('mfUpdateText'),dismiss=document.getElementById('mfUpdateDismiss'),dataLink=document.getElementById('mfUpdateDataLink'),productLink=document.getElementById('mfUpdateProductLink');
if(!box)return;
const read=()=>{{try{{return JSON.parse(localStorage.getItem(KEY)||'null')}}catch{{return null}}}};
const save=v=>{{try{{localStorage.setItem(KEY,JSON.stringify(v))}}catch{{}}}};
fetch(PREFIX+'data/build-info.json',{{cache:'no-store'}}).then(r=>r.ok?r.json():Promise.reject()).then(info=>{{
 const current={{schema:1,release_id:info.product_release?.release_id||null,source_updated:info.source_updated||null,patch:info.patch||null}};
 const prev=read();
 if(!prev||prev.schema!==1){{save(current);return}}
 const releaseChanged=prev.release_id!==current.release_id;
 const sourceChanged=prev.source_updated!==current.source_updated;
 const patchChanged=prev.patch!==current.patch;
 if(!releaseChanged&&!sourceChanged&&!patchChanged)return;
 const dataChanged=sourceChanged||patchChanged;
 const notes=[];
 if(patchChanged)notes.push(`Patch ${{prev.patch||'—'}} → ${{current.patch||'—'}}`);
 else if(sourceChanged)notes.push('La fuente publicó una medición nueva');
 if(releaseChanged)notes.push(`Nueva versión: ${{info.product_release?.title||current.release_id||'Meta Forge'}}`);
 title.textContent=dataChanged&&releaseChanged?'Datos y producto actualizados':patchChanged?'Nuevo patch detectado':sourceChanged?'Nuevo snapshot real':'Meta Forge se actualizó';
 text.textContent=notes.join(' · ')+'.';
 dataLink.hidden=!dataChanged;dataLink.href=PREFIX+'trends/';
 productLink.hidden=!releaseChanged;productLink.href=PREFIX+'status/';
 const mark=()=>save(current);dismiss.addEventListener('click',()=>{{mark();box.hidden=true}});dataLink.addEventListener('click',mark);productLink.addEventListener('click',mark);
 box.hidden=false;
}}).catch(()=>{{}});
}})();</script>'''

changed=0
for path,prefix in TARGETS.items():
    if not path.exists():
        raise RuntimeError(f'Update beacon target missing: {path}')
    text=path.read_text(encoding='utf-8')
    if 'id="mfUpdateBeacon"' in text:
        continue
    if '</head>' not in text or '</body>' not in text:
        raise RuntimeError(f'Update beacon target has invalid HTML shell: {path}')
    runtime=RUNTIME_TMPL.format(prefix=prefix)
    text=text.replace('</head>',STYLE+'</head>',1)
    text=text.replace('</body>',MARKUP+runtime+'</body>',1)
    path.write_text(text,encoding='utf-8')
    changed+=1

privacy=Path('privacy.html')
if not privacy.exists(): raise RuntimeError('privacy.html missing')
p=privacy.read_text(encoding='utf-8')
old='La web puede usar almacenamiento local del navegador para funciones como Watchlist, preferencias de perfil, historial local de drafts y comparaciones recientes. Esa información permanece en tu dispositivo y no se envía a un servidor propio de Meta Forge.'
new='La web puede usar almacenamiento local del navegador para funciones como Watchlist, preferencias de perfil, historial local de drafts, comparaciones recientes y el estado de novedades que ya marcaste como vistas. Esa información permanece en tu dispositivo y no se envía a un servidor propio de Meta Forge.'
if old in p:p=p.replace(old,new,1)
elif 'estado de novedades que ya marcaste como vistas' not in p:raise RuntimeError('Privacy local-storage disclosure anchor missing')
privacy.write_text(p,encoding='utf-8')
print(f'Update beacon injected: surfaces={changed}/5; key=mf_seen_updates_v1; compares=release_id/source_updated/patch; fetched_at_ignored=true; local_only=true')
