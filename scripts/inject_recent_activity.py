from pathlib import Path

ROOT=Path('.')
HOME=Path('index.html')
CORE={
    Path('index.html'):('home','Inicio',''),
    Path('roster/index.html'):('surface','Live Roster','roster/'),
    Path('explore/index.html'):('surface','Meta Explorer','explore/'),
    Path('trends/index.html'):('surface','Trends','trends/'),
    Path('compare/index.html'):('surface','Hero Compare','compare/'),
    Path('my-meta/index.html'):('surface','Mi Meta','my-meta/'),
}

if not HOME.exists():
    raise RuntimeError('Homepage is required for recent activity')

stats=sorted(Path('stats/heroes').glob('*/index.html'))
editorial=sorted(Path('heroes').glob('*/index.html'))
if len(stats)!=133:
    raise RuntimeError(f'Recent activity requires 133 live hero pages, found {len(stats)}')
if len(editorial)!=34:
    raise RuntimeError(f'Recent activity requires 34 editorial hero pages, found {len(editorial)}')

STYLE='''<style id="mf-recent-activity-style">.mf-resume{width:min(1180px,calc(100% - 28px));margin:10px auto 0;padding:14px 16px;border:1px solid #263a55;border-radius:18px;background:#09121f}.mf-resume[hidden]{display:none!important}.mf-resume-head{display:flex;align-items:center;justify-content:space-between;gap:12px}.mf-resume-head small{color:#8ba0bc;font-size:8px;font-weight:950;letter-spacing:.13em}.mf-resume-head h3{margin:3px 0 0;font-size:15px}.mf-resume-clear{border:1px solid #2d415d;border-radius:9px;background:#0c1726;color:#8fa2bc;padding:7px 9px;font:800 9px/1 system-ui;cursor:pointer}.mf-resume-list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:10px}.mf-resume-link{min-width:0;padding:10px 11px;border:1px solid #243955;border-radius:12px;background:#0b1625;color:#e8f2ff;text-decoration:none}.mf-resume-link:hover,.mf-resume-link:focus-visible{outline:none;border-color:#54e4ff;background:#0e1d30}.mf-resume-link b{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:11px}.mf-resume-link span{display:block;margin-top:4px;color:#7488a6;font-size:8px}.mf-resume-note{margin:8px 0 0;color:#6f829f;font-size:8px;line-height:1.4}@media(max-width:640px){.mf-resume-list{display:flex;overflow:auto;scroll-snap-type:x mandatory}.mf-resume-link{min-width:180px;scroll-snap-align:start}}</style>'''
PANEL='''<section id="mfResumePanel" class="mf-resume" hidden aria-labelledby="mfResumeTitle"><div class="mf-resume-head"><div><small>VUELVE AL PUNTO EXACTO</small><h3 id="mfResumeTitle">Continuar donde lo dejaste</h3></div><button id="mfResumeClear" class="mf-resume-clear" type="button">Borrar recientes</button></div><div id="mfResumeList" class="mf-resume-list"></div><p class="mf-resume-note">Este historial vive solo en tu navegador y guarda como máximo 8 destinos recientes.</p></section>'''

RUNTIME='''<script id="mf-recent-activity-runtime">(()=>{const KEY='mf_recent_activity_v1',LIMIT=8,IS_HOME=__IS_HOME__,KIND=__KIND__,BASE_ROUTE=__ROUTE__,FALLBACK_LABEL=__LABEL__;const read=()=>{try{const v=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(v)?v:[]}catch{return []}};const write=v=>{try{localStorage.setItem(KEY,JSON.stringify(v.slice(0,LIMIT)))}catch{}};const safeRoute=v=>typeof v==='string'&&/^(?:roster|explore|trends|compare|my-meta)\/(?:\?[^#]*)?$|^(?:stats\/heroes|heroes)\/[a-z0-9-]+\/(?:\?[^#]*)?$/.test(v);const currentLabel=()=>{const h=document.querySelector('h1');const v=(h?.textContent||FALLBACK_LABEL||'Meta Forge').trim().replace(/\s+/g,' ');return v.slice(0,80)};function record(){if(IS_HOME||!BASE_ROUTE)return;const route=BASE_ROUTE+(location.search||'');const entry={schema:1,key:BASE_ROUTE,label:currentLabel(),route,kind:KIND,ts:Date.now()};const old=read().filter(x=>x&&x.schema===1&&x.key!==BASE_ROUTE&&safeRoute(x.route));write([entry,...old])}function render(){if(!IS_HOME)return;const box=document.getElementById('mfResumePanel'),list=document.getElementById('mfResumeList'),clear=document.getElementById('mfResumeClear');if(!box||!list)return;const items=read().filter(x=>x&&x.schema===1&&safeRoute(x.route)&&typeof x.label==='string').slice(0,3);if(!items.length){box.hidden=true;return}list.replaceChildren();items.forEach(item=>{const a=document.createElement('a');a.className='mf-resume-link';a.href=item.route;const b=document.createElement('b');b.textContent=item.label;const s=document.createElement('span');s.textContent=item.kind==='hero'?'Héroe reciente':'Herramienta reciente';a.append(b,s);list.appendChild(a)});box.hidden=false;if(clear)clear.onclick=()=>{try{localStorage.removeItem(KEY)}catch{}list.replaceChildren();box.hidden=true}}record();render();if(!IS_HOME)addEventListener('pagehide',record,{once:true})})();</script>'''

def route_for(path):
    rel=path.as_posix()
    if rel.startswith('stats/heroes/'):
        return rel[:-10] if rel.endswith('index.html') else rel
    if rel.startswith('heroes/'):
        return rel[:-10] if rel.endswith('index.html') else rel
    return ''

def inject(path,kind,label,route):
    text=path.read_text(encoding='utf-8')
    if 'id="mf-recent-activity-runtime"' in text:
        return False
    runtime=(RUNTIME
        .replace('__IS_HOME__','true' if path==HOME else 'false')
        .replace('__KIND__',repr(kind))
        .replace('__ROUTE__',repr(route))
        .replace('__LABEL__',repr(label)))
    if '</body>' not in text:
        raise RuntimeError(f'Invalid HTML shell for recent activity: {path}')
    text=text.replace('</body>',runtime+'</body>',1)
    path.write_text(text,encoding='utf-8')
    return True

# The resume panel sits directly after the homepage decision hub.
home=HOME.read_text(encoding='utf-8')
if 'id="mfResumePanel"' not in home:
    marker='id="homeProductHub"'
    start=home.find(marker)
    if start<0:
        raise RuntimeError('Homepage product hub must exist before recent activity')
    end=home.find('</section>',start)
    if end<0:
        raise RuntimeError('Homepage product hub closing section missing')
    home=home[:end+10]+PANEL+home[end+10:]
    home=home.replace('</head>',STYLE+'</head>',1)
    HOME.write_text(home,encoding='utf-8')

changed=0
for path,(kind,label,route) in CORE.items():
    if not path.exists(): raise RuntimeError(f'Recent activity core target missing: {path}')
    changed+=int(inject(path,kind,label,route))
for path in stats:
    changed+=int(inject(path,'hero','Héroe',route_for(path)))
for path in editorial:
    changed+=int(inject(path,'hero','Héroe',route_for(path)))

privacy=Path('privacy.html')
if not privacy.exists(): raise RuntimeError('privacy.html missing')
p=privacy.read_text(encoding='utf-8')
if 'historial reciente para “Continuar donde lo dejaste”' not in p:
    old='La web puede usar almacenamiento local del navegador para funciones como Watchlist, preferencias de perfil, historial local de drafts, comparaciones recientes y el estado de novedades que ya marcaste como vistas. Esa información permanece en tu dispositivo y no se envía a un servidor propio de Meta Forge.'
    new='La web puede usar almacenamiento local del navegador para funciones como Watchlist, preferencias de perfil, historial local de drafts, comparaciones recientes, historial reciente para “Continuar donde lo dejaste” y el estado de novedades que ya marcaste como vistas. Esa información permanece en tu dispositivo y no se envía a un servidor propio de Meta Forge.'
    if old not in p:
        raise RuntimeError('Privacy disclosure anchor missing after update-beacon injection')
    p=p.replace(old,new,1)
    privacy.write_text(p,encoding='utf-8')

print(f'Recent activity injected: targets={changed}; core={len(CORE)}; live_heroes={len(stats)}; editorial_heroes={len(editorial)}; local_only=true; max_history=8; homepage_cards=3')
