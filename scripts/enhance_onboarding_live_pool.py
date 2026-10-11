from pathlib import Path
import json,re,unicodedata

INDEX=Path('index.html')
LIVE=Path('data/live-meta.json')
CAT=Path('data/hero-catalog.json')

for p in [INDEX,LIVE,CAT]:
    if not p.exists():
        raise RuntimeError(f'Missing onboarding dependency: {p}')

def norm(s):
    s=str(s or '').lower().replace('&','and')
    s=''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','',s)

html=INDEX.read_text(encoding='utf-8')
if 'id="mfOnboarding"' not in html:
    raise RuntimeError('Personalized onboarding must be injected before live-pool enhancement')
if 'window.MF_ONBOARD_HEROES=' in html:
    print('Live onboarding pool already injected')
    raise SystemExit

live=json.loads(LIVE.read_text(encoding='utf-8'))
catalog=json.loads(CAT.read_text(encoding='utf-8'))
live_heroes=[h for h in live.get('heroes',[]) if h.get('name')]
editorial={norm(h['name']):h for h in catalog.get('heroes',[]) if h.get('name')}
if len(live_heroes)<100:
    raise RuntimeError(f'Live onboarding requires full roster, found {len(live_heroes)} heroes')
if len(editorial)!=34:
    raise RuntimeError(f'Editorial catalog must contain 34 unique normalized heroes, found {len(editorial)}')

pool=[]
seen=set()
matched_editorial=0
for h in sorted(live_heroes,key=lambda x:x['name'].lower()):
    name=h['name']
    key=norm(name)
    if key in seen:
        raise RuntimeError(f'Duplicate normalized live hero in onboarding pool: {name}')
    seen.add(key)
    e=editorial.get(key)
    if e: matched_editorial+=1
    pool.append({
        'name':name,
        'wr':h.get('wr'),
        'ban':h.get('ban'),
        'pick':h.get('pick'),
        'lane':e.get('lane') if e else None,
        'editorial':bool(e),
        'editorial_name':e.get('name') if e else None,
    })

if matched_editorial!=34:
    missing=sorted(h['name'] for h in catalog.get('heroes',[]) if norm(h.get('name')) not in seen)
    raise RuntimeError(f'Only {matched_editorial}/34 editorial heroes matched live onboarding roster; missing={missing}')

payload=json.dumps(pool,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
script_marker="<script>\n(()=>{\nconst PROFILE='mf_profile_v1',WATCH='mf_watchlist_v1';"
if script_marker not in html:
    raise RuntimeError('Onboarding runtime marker missing')
prelude=f'<script>window.MF_ONBOARD_HEROES={payload};</script>'
html=html.replace(script_marker,prelude+script_marker,1)

old="const heroes=(window.DATA?.heroes||((typeof DATA!=='undefined'&&DATA?.heroes)?DATA.heroes:[]));"
new="const heroes=(window.MF_ONBOARD_HEROES||window.DATA?.heroes||((typeof DATA!=='undefined'&&DATA?.heroes)?DATA.heroes:[]));"
if old not in html:
    raise RuntimeError('Onboarding hero source marker missing')
html=html.replace(old,new,1)

old_choice="<span>${h.lane||''} · ${Number.isFinite(h.wr)?h.wr.toFixed(2)+'% WR':'—'}</span>"
new_choice="<span>${h.lane?h.lane+' · ':''}${Number.isFinite(h.wr)?h.wr.toFixed(2)+'% WR':'—'}${h.editorial?' · editorial':''}</span>"
if old_choice not in html:
    raise RuntimeError('Onboarding hero-choice metadata marker missing')
html=html.replace(old_choice,new_choice,1)

html=html.replace('id="mfOnboarding" class="onboarding"',f'id="mfOnboarding" data-onboarding-live="{len(pool)}" class="onboarding"',1)
html=html.replace('Elige tu rol principal y entre 3 y 5 héroes favoritos. Todo se guarda únicamente en este navegador.','Elige tu rol principal y entre 3 y 5 héroes favoritos del roster live. Todo se guarda únicamente en este navegador.',1)

INDEX.write_text(html,encoding='utf-8')
print(f'Enhanced onboarding with {len(pool)} live heroes; {matched_editorial}/34 matched normalized editorial profiles')
