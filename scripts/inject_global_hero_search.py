from pathlib import Path
import json, re, unicodedata

LIVE=Path('data/live-meta.json')
CORE=Path('data/editorial-core.json')
if not LIVE.exists():
    raise RuntimeError('data/live-meta.json is required for global hero search')

data=json.loads(LIVE.read_text(encoding='utf-8'))
heroes=data.get('heroes',[])
if len(heroes)<100:
    raise RuntimeError(f'Expected at least 100 live heroes, got {len(heroes)}')

editorial=set()
if CORE.exists():
    core=json.loads(CORE.read_text(encoding='utf-8'))
    profiles=core.get('profiles',{})
    if isinstance(profiles,dict): editorial.update(profiles.keys())

# Fallback to generated editorial folders if the core schema changes.
if not editorial and Path('heroes').exists():
    editorial={p.parent.name for p in Path('heroes').glob('*/index.html')}

def slugify(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')

items=[]
for h in heroes:
    name=h.get('name')
    if not name: continue
    slug=slugify(name)
    # editorial may be keyed by hero name; generated-folder fallback is slug based.
    has_editorial=(name in editorial) or (slug in editorial)
    items.append({
        'name':name,
        'slug':slug,
        'wr':h.get('wr'),
        'ban':h.get('ban'),
        'pick':h.get('pick'),
        'editorial':bool(has_editorial),
    })
items.sort(key=lambda x:x['name'].lower())
DATA=json.dumps(items,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')

CSS='''<style id="global-hero-search-style">
.ghs-launch{position:fixed;right:18px;top:18px;z-index:1200;border:1px solid #2a3c5c;background:#0a1322e8;color:#ddecff;border-radius:13px;padding:10px 12px;font:800 12px/1 system-ui;box-shadow:0 10px 30px #0007;backdrop-filter:blur(12px);cursor:pointer}.ghs-launch:hover,.ghs-launch:focus-visible{border-color:#50ddff;outline:none;box-shadow:0 0 0 3px #50ddff20,0 10px 30px #0007}.ghs-kbd{color:#7e91ae;margin-left:8px;font-weight:700}.ghs-dialog{width:min(720px,calc(100vw - 28px));max-height:min(78vh,720px);padding:0;border:1px solid #2b3d5d;border-radius:22px;background:#07101cf5;color:#eef5ff;box-shadow:0 30px 90px #000b;overflow:hidden}.ghs-dialog::backdrop{background:#02050acc;backdrop-filter:blur(4px)}.ghs-head{padding:16px;border-bottom:1px solid #1f304c}.ghs-top{display:flex;gap:10px;align-items:center}.ghs-input{flex:1;min-width:0;border:1px solid #2a3d5d;background:#0c1728;color:#eef5ff;border-radius:14px;padding:13px 14px;font:700 15px system-ui;outline:none}.ghs-input:focus{border-color:#52dcff;box-shadow:0 0 0 3px #52dcff1d}.ghs-close{border:0;background:#111d30;color:#aebcd2;border-radius:12px;padding:11px 12px;cursor:pointer}.ghs-help{margin:9px 2px 0;color:#7588a6;font:500 11px/1.45 system-ui}.ghs-results{padding:8px;overflow:auto;max-height:58vh}.ghs-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:center;padding:11px 12px;border-radius:14px;color:#eaf3ff;text-decoration:none;border:1px solid transparent}.ghs-row:hover,.ghs-row:focus-visible,.ghs-row[data-active="1"]{background:#0d1a2d;border-color:#263c5e;outline:none}.ghs-name{font:850 14px/1.2 system-ui}.ghs-meta{margin-top:5px;color:#8396b4;font:600 11px/1.3 system-ui}.ghs-stats{display:flex;gap:7px;align-items:center;justify-content:flex-end;flex-wrap:wrap}.ghs-stat,.ghs-editorial{padding:5px 7px;border-radius:999px;border:1px solid #263a59;background:#0a1424;color:#aebed5;font:800 10px/1 system-ui;white-space:nowrap}.ghs-editorial{border-color:#795cc080;color:#c9adff;background:#25194099}.ghs-empty{padding:28px;text-align:center;color:#7f90aa;font:600 13px/1.5 system-ui}.ghs-foot{padding:10px 16px;border-top:1px solid #1f304c;color:#6f819d;font:600 10px/1.4 system-ui}.ghs-foot b{color:#8fa2be}@media(max-width:700px){.ghs-launch{top:auto;right:12px;bottom:76px}.ghs-kbd{display:none}.ghs-dialog{border-radius:18px}.ghs-row{grid-template-columns:1fr}.ghs-stats{justify-content:flex-start}}
</style>'''

JS_TEMPLATE='''<script id="global-hero-search-script">
(()=>{
const HEROES=__DATA__;
const ROOT=__ROOT__;
const $=s=>document.querySelector(s);
const norm=s=>(s||'').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
const pct=v=>Number.isFinite(v)?v.toFixed(2)+'%':'—';
const dlg=$('#globalHeroSearch'); const input=$('#globalHeroSearchInput'); const results=$('#globalHeroSearchResults');
if(!dlg||!input||!results)return;
let visible=[]; let active=0;
function render(){
  const q=norm(input.value.trim());
  visible=HEROES.filter(h=>!q||norm(h.name).includes(q)).slice(0,18);
  active=0;
  if(!visible.length){results.innerHTML='<div class="ghs-empty">No encontré ese héroe en el snapshot live.</div>';return;}
  results.innerHTML=visible.map((h,i)=>`<a class="ghs-row" data-active="${i===0?1:0}" href="${ROOT}roster/${h.slug}/"><div><div class="ghs-name">${h.name}</div><div class="ghs-meta">Ficha estadística live${h.editorial?' · análisis editorial disponible':''}</div></div><div class="ghs-stats"><span class="ghs-stat">WR ${pct(h.wr)}</span><span class="ghs-stat">BAN ${pct(h.ban)}</span><span class="ghs-stat">PICK ${pct(h.pick)}</span>${h.editorial?'<span class="ghs-editorial">EDITORIAL</span>':''}</div></a>`).join('');
}
function openSearch(){if(!dlg.open)dlg.showModal();input.value='';render();setTimeout(()=>input.focus(),0)}
function closeSearch(){if(dlg.open)dlg.close()}
function move(dir){if(!visible.length)return;active=(active+dir+visible.length)%visible.length;[...results.querySelectorAll('.ghs-row')].forEach((el,i)=>el.dataset.active=i===active?'1':'0');results.querySelectorAll('.ghs-row')[active]?.scrollIntoView({block:'nearest'})}
document.querySelectorAll('[data-global-hero-search]').forEach(b=>b.addEventListener('click',openSearch));
$('#globalHeroSearchClose')?.addEventListener('click',closeSearch);
input.addEventListener('input',render);
input.addEventListener('keydown',e=>{if(e.key==='ArrowDown'){e.preventDefault();move(1)}else if(e.key==='ArrowUp'){e.preventDefault();move(-1)}else if(e.key==='Enter'&&visible.length){e.preventDefault();location.href=ROOT+'roster/'+visible[active].slug+'/'}else if(e.key==='Escape'){closeSearch()}});
document.addEventListener('keydown',e=>{const tag=(e.target?.tagName||'').toLowerCase();const typing=['input','textarea','select'].includes(tag)||e.target?.isContentEditable;if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();openSearch()}else if(!typing&&e.key==='/'&&!dlg.open){e.preventDefault();openSearch()}});
dlg.addEventListener('click',e=>{if(e.target===dlg)closeSearch()});
})();
</script>'''

BUTTON='''<button class="ghs-launch" type="button" data-global-hero-search aria-label="Buscar entre todos los héroes">⌕ Buscar héroe <span class="ghs-kbd">Ctrl K</span></button>'''
DIALOG='''<dialog id="globalHeroSearch" class="ghs-dialog" aria-label="Buscar héroe"><div class="ghs-head"><div class="ghs-top"><input id="globalHeroSearchInput" class="ghs-input" type="search" autocomplete="off" placeholder="Escribe un héroe…" aria-label="Nombre del héroe"><button id="globalHeroSearchClose" class="ghs-close" type="button" aria-label="Cerrar">✕</button></div><div class="ghs-help">Busca en el roster live completo. Enter abre la ficha estadística. Usa ↑ ↓ para moverte.</div></div><div id="globalHeroSearchResults" class="ghs-results" role="listbox"></div><div class="ghs-foot"><b>LIVE</b> = estadísticas del snapshot · <b>EDITORIAL</b> = además tiene análisis curado de Meta Forge</div></dialog>'''

TARGETS={
    Path('index.html'):'./',
    Path('trends/index.html'):'../',
    Path('my-meta/index.html'):'../',
    Path('roster/index.html'):'../',
}
changed=0
for path,root in TARGETS.items():
    if not path.exists():
        raise RuntimeError(f'Missing global-search target: {path}')
    html=path.read_text(encoding='utf-8')
    if 'id="globalHeroSearch"' in html:
        continue
    if '</head>' not in html or '</body>' not in html:
        raise RuntimeError(f'Unexpected HTML structure in {path}')
    js=JS_TEMPLATE.replace('__DATA__',DATA).replace('__ROOT__',json.dumps(root))
    html=html.replace('</head>',CSS+'</head>',1)
    html=html.replace('</body>',BUTTON+DIALOG+js+'</body>',1)
    path.write_text(html,encoding='utf-8')
    changed+=1

if changed and changed != len(TARGETS):
    raise RuntimeError(f'Global hero search injected into only {changed}/{len(TARGETS)} pages')
print(f'Global hero search ready for {len(items)} heroes across {len(TARGETS)} surfaces')
