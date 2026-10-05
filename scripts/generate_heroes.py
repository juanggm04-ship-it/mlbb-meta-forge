from pathlib import Path
from html import escape
import re, unicodedata

BASE='https://juanggm04-ship-it.github.io/mlbb-meta-forge/'
UPDATED='5 oct 2026'
PATCH='2.2.16'
HEROES=[
('Aulus','Jungle','S+',59.53,18.62,'Fighter','Escalado brutal y gran consistencia en ranked.'),
('Rafaela','Roam','S+',59.38,16.71,'Support','Sustain, velocidad y resets de pelea muy valiosos.'),
('Masha','EXP','S+',59.17,27.87,'Fighter','Presión lateral, aguante y amenaza sobre backline.'),
('Marcel','Roam','S+',58.07,32.76,'Support','Utilidad y control que condicionan la fase de draft.'),
('Argus','EXP','S+',55.52,None,'Fighter','Duelista de alta presión y excelente capacidad de cierre.'),
('Minotaur','Roam','S+',55.02,None,'Tank/Support','Engage fiable y protección para composiciones front-to-back.'),
('Khufra','Roam','S+',54.57,None,'Tank','Castiga movilidad y ofrece iniciación muy clara.'),
('Floryn','Roam','S+',54.18,None,'Support','Curación global y sustain excelente en peleas extendidas.'),
('Gloo','EXP','S+',53.90,38.61,'Tank','Frontline flexible con mucha disrupción en peleas largas.'),
('Carmilla','Roam','S+',53.74,None,'Support/Tank','Gran valor cuando puede enlazar daño y control sobre varios rivales.'),
('Obsidia','Gold','S+',53.50,None,'Marksman','Carry de Gold con presencia estable en el parche.'),
('Hirara','Jungle','S+',53.39,66.43,'Assassin','La mayor presión de ban del pool observado; define drafts.'),
('Estes','Roam','S+',53.06,38.27,'Support','Sustain enorme si el rival no puede cortar curación y formación.'),
('Popol & Kupa','Gold','A',54.27,None,'Marksman','Control de espacio y presión temprana de objetivos.'),
('Lolita','Roam','A',54.05,None,'Tank/Support','Peel y protección muy fuertes contra proyectiles.'),
('Valir','Mid','A',53.46,None,'Mage','Control de zona y disengage para proteger carries.'),
('Diggie','Roam','A',53.38,None,'Support','Respuesta premium frente a composiciones dependientes de control.'),
('Bruno','Gold','A',53.11,None,'Marksman','Daño crítico y gran amenaza si consigue ventaja de oro.'),
('Lukas','EXP','A',52.98,29.92,'Fighter','Pick flexible con presencia sostenida y presión en skirmishes.'),
('Gord','Mid','A',52.87,None,'Mage','Poke y control de zonas estrechas alrededor de objetivos.'),
('Edith','EXP','A',52.70,None,'Tank/Marksman','Frontline con amenaza de daño cuando cambia de forma.'),
('Cyclops','Mid','A',52.65,None,'Mage','Daño sostenido y buen castigo a objetivos aislados.'),
('Belerick','Roam','A',52.46,None,'Tank','Excelente contra composiciones de ataques repetidos.'),
('Ruby','EXP','A',52.33,None,'Fighter/Tank','Control constante y sustain en peleas extendidas.'),
('Hanabi','Gold','A',52.09,None,'Marksman','Buen daño en peleas agrupadas cuando mantiene posición.'),
('Eudora','Mid','A',51.24,59.16,'Mage','Amenaza de burst que comprime el posicionamiento rival.'),
('Granger','Gold','A',51.80,None,'Marksman','Burst físico y movilidad para castigar ventanas cortas.'),
('Hayabusa','Jungle','A',51.72,None,'Assassin','Amenaza de split y ejecución sobre backline aislada.'),
('Nolan','Jungle','A',51.67,None,'Assassin','Tempo alto y buen control de ritmo desde la jungla.'),
('Tigreal','Roam','A',51.41,None,'Tank','Engage directo y fácil de coordinar en ranked.'),
('Xavier','Mid','A',51.30,None,'Mage','Poke global y escalado para composiciones front-to-back.'),
('Ixia','Gold','A',51.14,None,'Marksman','Teamfight fuerte si dispone de frontline y espacio.'),
('Fredrinn','Jungle','A',50.88,None,'Tank/Fighter','Jungla resistente con buena presencia en objetivos.'),
('Pharsa','Mid','A',50.73,None,'Mage','Artillería de largo alcance y rotaciones rápidas.')]

BY_NAME={h[0]:h for h in HEROES}

def slugify(name):
    s=''.join(c for c in unicodedata.normalize('NFD',name.lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')

def pct(v): return f'{v:.2f}%' if v is not None else '—'

def first_existing(names, current, limit=3):
    out=[]
    for n in names:
        if n != current and n in BY_NAME and n not in out:
            out.append(n)
        if len(out)>=limit: break
    return out

def recommendations(h):
    name,lane,tier,wr,ban,role,note=h
    role_l=role.lower()
    if lane=='Gold':
        sy=first_existing(['Minotaur','Rafaela','Lolita','Tigreal','Valir'],name)
        threats=first_existing(['Hayabusa','Nolan','Hirara','Eudora','Khufra'],name)
        reason='Los tiradores suelen rendir mejor con frontline y peel; sufren cuando el rival accede rápido a la retaguardia.'
    elif lane=='Mid':
        sy=first_existing(['Khufra','Minotaur','Tigreal','Fredrinn','Ruby'],name)
        threats=first_existing(['Hayabusa','Nolan','Hirara','Masha','Argus'],name)
        reason='Los mids ganan valor cuando alguien fija objetivos; la movilidad y el dive rival reducen su espacio para castear.'
    elif lane=='Jungle':
        sy=first_existing(['Khufra','Minotaur','Rafaela','Valir','Carmilla'],name)
        threats=first_existing(['Valir','Khufra','Diggie','Eudora','Belerick'],name)
        reason='El jungla agradece control e iniciación para convertir tempo en objetivos; peel, anti-dash y burst pueden frenar entradas agresivas.'
    elif lane=='EXP':
        sy=first_existing(['Rafaela','Carmilla','Minotaur','Xavier','Bruno'],name)
        threats=first_existing(['Valir','Eudora','Gloo','Ruby','Khufra'],name)
        reason='EXP suele funcionar como presión lateral o segunda frontline; control de zona y burst pueden castigar entradas o alargar duelos desfavorables.'
    else:
        sy=first_existing(['Bruno','Ixia','Aulus','Xavier','Masha'],name)
        threats=first_existing(['Diggie','Valir','Eudora','Masha','Hayabusa'],name)
        reason='El roam multiplica el valor de carries que aprovechan su engage, peel o sustain; respuestas anti-CC, poke o dive pueden reducir ese impacto.'
    if 'assassin' in role_l:
        threats=first_existing(['Khufra','Valir','Diggie','Eudora','Belerick'],name)
    if 'tank' in role_l and lane=='Roam':
        sy=first_existing(['Bruno','Ixia','Xavier','Aulus','Obsidia'],name)
    return sy, threats, reason

CSS='''body{margin:0;background:radial-gradient(circle at 12% 0%,#17264a 0,transparent 30%),#070a12;color:#eef4ff;font-family:system-ui;padding:28px 18px}main{max-width:930px;margin:auto}a{color:#46e6ff;text-decoration:none}.hero{margin-top:22px;padding:30px;border:1px solid #263552;background:linear-gradient(135deg,#111b30,#18132d);border-radius:28px}.badge{display:inline-block;padding:7px 10px;border:1px solid #46e6ff55;border-radius:999px;color:#46e6ff;font-size:12px;font-weight:800}h1{font-size:clamp(42px,8vw,72px);letter-spacing:-.06em;margin:14px 0}h2{letter-spacing:-.03em}p{color:#a8b6ce;line-height:1.7}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:22px}.stat,.box,.card{background:#0d1423;border:1px solid #22304b;border-radius:18px;padding:18px}.stat b{display:block;font-size:24px}.stat span,.label{font-size:10px;color:#8190aa;letter-spacing:.08em;font-weight:800}.box{margin-top:18px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:20px}.card b{display:block;font-size:20px}.card span{font-size:12px;color:#8fa0bc}.pairs{display:grid;grid-template-columns:1fr 1fr;gap:12px}.chips{display:flex;gap:8px;flex-wrap:wrap}.chip{display:inline-flex;padding:9px 11px;border:1px solid #2c3d5b;border-radius:12px;background:#10192a;color:#dbe7fb;font-size:13px}.editorial{border-left:3px solid #ffcf57;padding-left:13px;color:#98a7c0}.cta{display:inline-flex;margin-top:12px;padding:11px 14px;border-radius:12px;background:linear-gradient(135deg,#46e6ff,#8b5cff);color:#07101d;font-weight:900}@media(max-width:700px){.stats,.grid,.pairs{grid-template-columns:1fr}}'''

def chips(names): return ''.join(f'<a class="chip" href="../{slugify(n)}/">{escape(n)}</a>' for n in names)

def hero_page(h):
    name,lane,tier,wr,ban,role,note=h; slug=slugify(name); sy,threats,reason=recommendations(h)
    desc=f'{name}: tier {tier}, win rate {pct(wr)}, {lane}. Snapshot S42 Patch {PATCH}.'
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(name)} MLBB · Win rate, tier y draft | Meta Forge</title><meta name="description" content="{escape(desc)}"><link rel="canonical" href="{BASE}heroes/{slug}/"><meta property="og:title" content="{escape(name)} · MLBB Meta Forge"><meta property="og:description" content="{escape(desc)}"><style>{CSS}</style></head><body><main><a href="../">← Todos los héroes</a><section class="hero"><span class="badge">{escape(lane)} · {escape(role)} · TIER {tier}</span><h1>{escape(name)}</h1><p>{escape(note)}</p><div class="stats"><div class="stat"><b>{pct(wr)}</b><span>WIN RATE</span></div><div class="stat"><b>{pct(ban)}</b><span>BAN RATE</span></div><div class="stat"><b>{tier}</b><span>TIER EDITORIAL</span></div></div></section><section class="box"><h2>Lectura del snapshot</h2><p>Todos los valores proceden del mismo snapshot usado en la portada: {UPDATED}, Season 42, Patch {PATCH}. El tier es una interpretación editorial. Si una métrica no está disponible, mostramos “—” en lugar de estimarla.</p></section><section class="pairs"><article class="box"><span class="label">SINERGIAS EDITORIALES</span><h2>Aliados que encajan</h2><div class="chips">{chips(sy)}</div></article><article class="box"><span class="label">AMENAZAS EDITORIALES</span><h2>Picks a respetar</h2><div class="chips">{chips(threats)}</div></article></section><section class="box"><h2>Por qué</h2><p>{escape(reason)}</p><p class="editorial"><strong>Importante:</strong> estas relaciones son recomendaciones editoriales basadas en funciones de draft y estilo de juego. No son porcentajes de matchup ni estadísticas de counter verificadas.</p></section><section class="box"><h2>Cómo interpretarlo</h2><p>El win rate no debe leerse aislado. Ban rate, rango, composición, matchup y dominio del héroe pueden cambiar su valor real en una partida concreta.</p><a class="cta" href="../../">Volver al Meta Forge</a></section></main></body></html>'''

root=Path('.')
hero_root=root/'heroes'; hero_root.mkdir(exist_ok=True)
for h in HEROES:
    d=hero_root/slugify(h[0]); d.mkdir(parents=True,exist_ok=True)
    (d/'index.html').write_text(hero_page(h),encoding='utf-8')

cards=''.join(f'<a class="card" href="{slugify(h[0])}/"><b>{escape(h[0])}</b><span>{escape(h[1])} · {h[2]} · {pct(h[3])} WR</span></a>' for h in sorted(HEROES,key=lambda x:-x[3]))
(hero_root/'index.html').write_text(f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Héroes MLBB · Meta Forge</title><meta name="description" content="Fichas de héroes MLBB con win rate, tier, sinergias y amenazas editoriales."><style>{CSS}</style></head><body><main><a href="../">← Meta Forge</a><section class="hero"><span class="badge">34 HÉROES · SNAPSHOT {UPDATED}</span><h1>Héroes del meta</h1><p>Fichas individuales generadas desde una única fuente de datos para evitar inconsistencias.</p></section><div class="grid">{cards}</div></main></body></html>''',encoding='utf-8')

# Mejora progresiva de la portada durante el build: añade navegación a la ficha completa
index_path=root/'index.html'
if index_path.exists():
    html=index_path.read_text(encoding='utf-8')
    marker='function fmtPct(v){return Number.isFinite(v)?v.toFixed(2)+\'%\':\'—\'}'
    slug_js="function heroSlug(n){return n.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').replace(/&/g,'and').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')}"
    if 'function heroSlug' not in html and marker in html:
        html=html.replace(marker,marker+'\n'+slug_js)
    old='<p class="note">Snapshot ${DATA.updated} · parche ${DATA.patch}. Todas las vistas usan este mismo valor de win rate.</p>`;heroDialog.showModal()}'
    new='<p class="note">Snapshot ${DATA.updated} · parche ${DATA.patch}. Todas las vistas usan este mismo valor de win rate.</p><div class="share-row"><a class="primary" href="heroes/${heroSlug(h.name)}/">Ver ficha completa →</a></div>`;heroDialog.showModal()}'
    if old in html:
        html=html.replace(old,new)
    index_path.write_text(html,encoding='utf-8')

urls=[BASE,BASE+'heroes/',BASE+'privacy.html',BASE+'terms.html']+[BASE+'heroes/'+slugify(h[0])+'/' for h in HEROES]
sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{u}</loc><lastmod>2026-10-05</lastmod></url>' for u in urls)+'</urlset>'
(root/'sitemap.xml').write_text(sitemap,encoding='utf-8')
print(f'Generated {len(HEROES)} hero pages, editorial synergies/threats, homepage links and sitemap')
