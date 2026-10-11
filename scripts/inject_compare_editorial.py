from pathlib import Path
import json

PAGE=Path('compare/index.html')
CORE=Path('data/editorial-core.json')
if not PAGE.exists() or not CORE.exists():
    raise RuntimeError('Hero Compare page and editorial core are required')

html=PAGE.read_text(encoding='utf-8')
core=json.loads(CORE.read_text(encoding='utf-8'))
profiles=core.get('profiles',{})
if len(profiles)<30:
    raise RuntimeError('Editorial core unexpectedly small')
if 'id="compareEditorial"' in html:
    print('Hero Compare editorial context already present')
    raise SystemExit

payload=json.dumps(profiles,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

css='''.editorial-compare{margin-top:18px;border-top:1px solid #283952;padding-top:16px}.editorial-head{display:flex;justify-content:space-between;gap:12px;align-items:end;flex-wrap:wrap}.editorial-grid{display:grid;gap:8px;margin-top:12px}.ed-row{display:grid;grid-template-columns:1fr 120px 1fr;gap:10px;align-items:center;padding:9px 10px;border:1px solid #22334d;border-radius:12px}.ed-side{display:flex;justify-content:flex-end;gap:6px;flex-wrap:wrap}.ed-side.right{justify-content:flex-start}.ed-chip{font-size:10px;padding:5px 8px;border:1px solid #324b6b;border-radius:999px;color:#8fa2bc}.ed-chip.on{color:#8af0c0;border-color:#386b5b;background:#10271f}.ed-label{text-align:center;color:#8193ad;font-size:10px}.editorial-empty{margin-top:12px;padding:14px;border:1px dashed #2d405c;border-radius:13px;color:#7486a2;font-size:11px}@media(max-width:700px){.ed-row{grid-template-columns:1fr 88px 1fr}.editorial-head{align-items:start}}'''
html=html.replace('</style>',css+'</style>',1)

marker='<div id="rows" class="compare"></div>'
block='''<div id="compareEditorial" class="editorial-compare"><div class="editorial-head"><div><div class="sub">EDITORIAL · SOLO SI AMBOS ESTÁN CURADOS</div><strong>Perfil estratégico comparado</strong></div><span class="sub">No modifica el Meta Score</span></div><div id="compareEditorialBody"></div></div>'''
if marker not in html:
    raise RuntimeError('Hero Compare rows marker missing')
html=html.replace(marker,marker+block,1)

js=f'''\nconst EDITORIAL_PROFILES={payload};\nconst editorialMetrics=[['front','Frontline'],['engage','Engage'],['sustain','Sustain'],['peel','Peel'],['dive','Dive'],['wave','Waveclear'],['scaling','Scaling'],['poke','Poke']];\nfunction edChip(on){{return `<span class="ed-chip ${{on?'on':''}}">${{on?'SÍ':'NO'}}</span>`}}\nfunction renderEditorial(a,b){{const root=document.getElementById('compareEditorialBody'),pa=EDITORIAL_PROFILES[a.name],pb=EDITORIAL_PROFILES[b.name];if(!root)return;if(!pa||!pb){{const missing=[!pa?a.name:null,!pb?b.name:null].filter(Boolean).join(' y ');root.innerHTML=`<div class="editorial-empty">Contexto editorial no disponible para ${{missing}}. La comparación superior sigue siendo válida como lectura estadística live; no rellenamos perfiles estratégicos que aún no están curados.</div>`;return}}const rows=editorialMetrics.map(([key,label])=>`<div class="ed-row"><div class="ed-side">${{edChip(!!pa[key])}}</div><div class="ed-label">${{label}}</div><div class="ed-side right">${{edChip(!!pb[key])}}</div></div>`).join('');const damage=`<div class="ed-row"><div class="ed-side">${{pa.phys?'<span class="ed-chip on">FÍSICO</span>':''}}${{pa.magic?'<span class="ed-chip on">MÁGICO</span>':''}}</div><div class="ed-label">Daño</div><div class="ed-side right">${{pb.phys?'<span class="ed-chip on">FÍSICO</span>':''}}${{pb.magic?'<span class="ed-chip on">MÁGICO</span>':''}}</div></div>`;root.innerHTML='<div class="editorial-grid">'+rows+damage+'</div>'}}\n'''
script_marker='const HEROES='
if script_marker not in html:
    raise RuntimeError('Hero Compare script marker missing')
html=html.replace(script_marker,js+script_marker,1)

render_marker="history.replaceState(null,'',u)}}"
if render_marker not in html:
    raise RuntimeError('Hero Compare render hook missing')
html=html.replace(render_marker,"history.replaceState(null,'',u);renderEditorial(a,b)}}",1)

PAGE.write_text(html,encoding='utf-8')
print(f'Injected optional editorial comparison for {len(profiles)} curated heroes')
