from pathlib import Path
import json

PAGE=Path('compare/index.html')
CORE=Path('data/editorial-core.json')
if not PAGE.exists() or not CORE.exists():
    raise RuntimeError('Hero Compare page and editorial core are required')

html=PAGE.read_text(encoding='utf-8')
core=json.loads(CORE.read_text(encoding='utf-8'))
matchups=core.get('matchups',{})
if len(matchups)<10:
    raise RuntimeError('Editorial matchup core unexpectedly small')
if 'id="compareMatchup"' in html:
    print('Hero Compare direct matchup context already present')
    raise SystemExit

payload=json.dumps(matchups,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
css='''.matchup-direct{margin-top:16px;padding:14px;border:1px solid #293d59;border-radius:16px;background:#09131f}.matchup-direct .tag{display:inline-block;font-size:9px;font-weight:900;letter-spacing:.09em;text-transform:uppercase;padding:5px 8px;border-radius:999px;border:1px solid #35506e;color:#9eb0c8}.matchup-direct.good{border-color:#2f6b58;background:#0d1c18}.matchup-direct.good .tag{border-color:#39705e;color:#8df0c2}.matchup-direct.warn{border-color:#71582e;background:#1d170d}.matchup-direct.warn .tag{border-color:#7c653b;color:#f0cf89}.matchup-direct h3{margin:9px 0 5px;font-size:16px}.matchup-direct p{margin:0;font-size:11px;color:#8394ad}.matchup-direct.neutral{border-style:dashed;color:#7789a4}'''
html=html.replace('</style>',css+'</style>',1)

marker='<div id="compareEditorialBody"></div>'
block='<div id="compareMatchup"></div>'
if marker not in html:
    raise RuntimeError('Editorial compare body marker missing')
html=html.replace(marker,marker+block,1)

js=f'''\nconst EDITORIAL_MATCHUPS={payload};\nfunction directMatchup(a,b){{\n  const ar=EDITORIAL_MATCHUPS[a.name]||{{}}, br=EDITORIAL_MATCHUPS[b.name]||{{}};\n  if((ar.good||[]).includes(b.name)) return ['good',`${{a.name}} puede castigar a ${{b.name}}`,'Lectura editorial favorable por acceso, rango o patrón de pelea.'];\n  if((ar.warn||[]).includes(b.name)) return ['warn',`${{a.name}} debe respetar a ${{b.name}}`,'El segundo héroe tiene herramientas editoriales que pueden limitar el plan del primero.'];\n  if((br.good||[]).includes(a.name)) return ['warn',`${{b.name}} puede castigar a ${{a.name}}`,'La relación explícita del core favorece al segundo héroe en esta interacción editorial.'];\n  if((br.warn||[]).includes(a.name)) return ['good',`${{a.name}} responde bien a ${{b.name}}`,'El core editorial marca herramientas útiles del primer héroe contra el patrón del segundo.'];\n  return null;\n}}\nfunction renderDirectMatchup(a,b){{\n  const root=document.getElementById('compareMatchup'); if(!root)return;\n  const m=directMatchup(a,b);\n  if(!m){{root.innerHTML='<div class="matchup-direct neutral"><span class="tag">SIN REGLA DIRECTA</span><h3>Sin interacción editorial explícita</h3><p>No inferimos un counter cuando el core no tiene una regla para esta pareja.</p></div>';return}}\n  root.innerHTML=`<div class="matchup-direct ${{m[0]}}"><span class="tag">INTERACCIÓN EDITORIAL</span><h3>${{m[1]}}</h3><p>${{m[2]}} No es counter-rate ni probabilidad de victoria.</p></div>`;\n}}\n'''
script_marker='const HEROES='
if script_marker not in html:
    raise RuntimeError('Hero Compare script marker missing')
html=html.replace(script_marker,js+script_marker,1)

hook='renderEditorial(a,b)}}'
if hook not in html:
    raise RuntimeError('Editorial render hook missing')
html=html.replace(hook,'renderEditorial(a,b);renderDirectMatchup(a,b)}}',1)

PAGE.write_text(html,encoding='utf-8')
print(f'Injected direct editorial matchup context from {len(matchups)} matchup rules')
