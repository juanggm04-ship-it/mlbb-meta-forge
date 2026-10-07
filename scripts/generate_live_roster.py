from pathlib import Path
from html import escape
import json, re, unicodedata, datetime

BASE='https://juanggm04-ship-it.github.io/mlbb-meta-forge/'
LIVE=Path('data/live-meta.json')
PREV=Path('data/previous-meta.json')
INDEX=Path('index.html')
SITEMAP=Path('sitemap.xml')


def slugify(name):
    s=''.join(c for c in unicodedata.normalize('NFD',str(name).lower()) if unicodedata.category(c)!='Mn')
    return re.sub(r'[^a-z0-9]+','-',s.replace('&','and')).strip('-')


def pct(v):
    return f'{v:.2f}%' if isinstance(v,(int,float)) else '—'


def fmt_time(value):
    if not value:return 'Fecha no disponible'
    try:
        d=datetime.datetime.fromisoformat(str(value).replace('Z','+00:00'))
        return d.strftime('%Y-%m-%d %H:%M UTC')
    except Exception:
        return str(value)


def load_json(path, fallback=None):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception:return fallback


def delta(cur, old):
    if not isinstance(cur,(int,float)) or not isinstance(old,(int,float)):return None
    return round(cur-old,2)


def delta_text(v):
    if not isinstance(v,(int,float)):return '—'
    return f'{v:+.2f} pp'


def data_source(meta):
    src=meta.get('source')
    if isinstance(src,dict) and src.get('name'):return str(src['name'])
    return str(meta.get('provider') or 'Fuente pública sincronizada')


def stat_page(hero, meta, previous_map, editorial_slugs):
    name=hero['name']; slug=slugify(name); prev=previous_map.get(name,{})
    dwr=delta(hero.get('wr'),prev.get('wr')); dban=delta(hero.get('ban'),prev.get('ban')); dpick=delta(hero.get('pick'),prev.get('pick'))
    editorial=slug in editorial_slugs
    editorial_cta=(f'<a class="btn alt" href="../../../heroes/{slug}/">Ver análisis editorial →</a>' if editorial else '')
    source=data_source(meta)
    fetched=fmt_time(meta.get('fetched_at'))
    patch=escape(str(meta.get('patch') or '—'))
    desc=f'{name}: WR {pct(hero.get("wr"))}, ban {pct(hero.get("ban"))}, pick {pct(hero.get("pick"))}. Snapshot público sincronizado.'
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(name)} stats MLBB | Meta Forge</title><meta name="description" content="{escape(desc)}"><link rel="canonical" href="{BASE}stats/heroes/{slug}/"><style>
body{{margin:0;background:radial-gradient(circle at 15% 0,#152644 0,transparent 30%),#070a12;color:#eef5ff;font-family:system-ui;padding:26px 18px}}main{{max-width:930px;margin:auto}}a{{color:#54e8ff;text-decoration:none}}.hero,.panel{{border:1px solid #263650;background:#0c1320;border-radius:24px;padding:24px;margin-top:18px}}h1{{font-size:clamp(40px,8vw,72px);letter-spacing:-.055em;margin:12px 0}}h2{{margin:0 0 12px}}p{{color:#9eacc4;line-height:1.65}}.badge{{display:inline-flex;padding:7px 10px;border:1px solid #42e5ff55;border-radius:999px;color:#57e9ff;font-size:11px;font-weight:900}}.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:20px}}.stat{{padding:18px;border:1px solid #22324b;border-radius:17px;background:#09111d}}.stat b{{font-size:27px;display:block}}.stat span{{display:block;color:#7e90ad;font-size:10px;margin-top:5px;letter-spacing:.08em}}.delta{{margin-top:7px;font-size:12px;color:#bdc9db}}.provenance{{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}}.pill{{border-radius:999px;padding:7px 10px;font-size:10px;font-weight:900;border:1px solid #2c425f}}.live{{color:#57e9ff}}.editorial{{color:#ffd36c}}.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}}.btn{{display:inline-flex;padding:11px 14px;border-radius:12px;background:linear-gradient(135deg,#4ae8ff,#8c5cff);color:#08101d;font-weight:900}}.btn.alt{{background:#111a2b;color:#eaf2ff;border:1px solid #2a3b58}}@media(max-width:680px){{.stats{{grid-template-columns:1fr}}}}</style></head><body><main><a href="../../../roster/">← Live Roster</a><section class="hero"><span class="badge">LIVE STATS · PATCH {patch}</span><h1>{escape(name)}</h1><p>Ficha estadística generada directamente desde el último snapshot público validado. No añade rol, tier, counters ni sinergias cuando esos datos no están presentes en la fuente.</p><div class="stats"><div class="stat"><b>{pct(hero.get('wr'))}</b><span>WIN RATE</span><div class="delta">vs. snapshot anterior: {delta_text(dwr)}</div></div><div class="stat"><b>{pct(hero.get('ban'))}</b><span>BAN RATE</span><div class="delta">vs. snapshot anterior: {delta_text(dban)}</div></div><div class="stat"><b>{pct(hero.get('pick'))}</b><span>PICK RATE</span><div class="delta">vs. snapshot anterior: {delta_text(dpick)}</div></div></div><div class="provenance"><span class="pill live">LIVE STATS · WR / BAN / PICK</span>{'<span class="pill editorial">EDITORIAL DISPONIBLE</span>' if editorial else ''}</div></section><section class="panel"><h2>Procedencia</h2><p><strong>Proveedor:</strong> {escape(str(meta.get('provider') or '—'))}<br><strong>Fuente declarada:</strong> {escape(source)}<br><strong>Consultado:</strong> {escape(fetched)}<br><strong>Fecha propia del dato:</strong> {escape(str(meta.get('source_updated') or 'no informada por la fuente'))}</p><div class="actions"><a class="btn" href="../../../roster/">Explorar los 133 héroes</a>{editorial_cta}</div></section></main></body></html>'''


def main():
    if not LIVE.exists():
        print('No live-meta.json; skipping full roster generation')
        return
    meta=load_json(LIVE,{}) or {}
    heroes=meta.get('heroes',[])
    if len(heroes)<100:raise RuntimeError(f'Live roster requires >=100 heroes, got {len(heroes)}')
    names=[h.get('name') for h in heroes if h.get('name')]
    if len(names)!=len(set(names)):raise RuntimeError('Duplicate hero names in live roster')
    heroes=[h for h in heroes if h.get('name') and isinstance(h.get('wr'),(int,float))]
    heroes.sort(key=lambda h:(-h.get('wr',0),h['name']))

    prev=load_json(PREV,{}) or {}
    previous_map={h.get('name'):h for h in prev.get('heroes',[]) if h.get('name')}
    editorial_slugs={p.parent.name for p in Path('heroes').glob('*/index.html')}

    stat_root=Path('stats/heroes');stat_root.mkdir(parents=True,exist_ok=True)
    for h in heroes:
        d=stat_root/slugify(h['name']);d.mkdir(parents=True,exist_ok=True)
        (d/'index.html').write_text(stat_page(h,meta,previous_map,editorial_slugs),encoding='utf-8')

    data=json.dumps([{'name':h['name'],'wr':h.get('wr'),'ban':h.get('ban'),'pick':h.get('pick'),'slug':slugify(h['name']),'editorial':slugify(h['name']) in editorial_slugs} for h in heroes],ensure_ascii=False,separators=(',',':'))
    roster=Path('roster');roster.mkdir(exist_ok=True)
    source=escape(data_source(meta)); fetched=escape(fmt_time(meta.get('fetched_at'))); patch=escape(str(meta.get('patch') or '—'))
    (roster/'index.html').write_text(f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Live Roster MLBB · 133 héroes | Meta Forge</title><meta name="description" content="Explora el roster completo del snapshot público de MLBB con win rate, ban rate y pick rate."><link rel="canonical" href="{BASE}roster/"><style>
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 15% 0,#152644 0,transparent 30%),#070a12;color:#eef5ff;font-family:system-ui}}main{{max-width:1180px;margin:auto;padding:28px 18px 70px}}a{{color:inherit;text-decoration:none}}.hero{{padding:28px;border:1px solid #263650;background:linear-gradient(145deg,#0c1422,#121226);border-radius:26px}}h1{{font-size:clamp(42px,8vw,78px);letter-spacing:-.06em;margin:10px 0}}p{{color:#9dacbf;line-height:1.6}}.badge,.pill{{display:inline-flex;border-radius:999px;padding:7px 10px;font-size:10px;font-weight:900;border:1px solid #2b405e}}.badge,.live{{color:#55e9ff}}.editorial{{color:#ffd36c}}.toolbar{{display:grid;grid-template-columns:1fr 190px;gap:10px;margin:18px 0}}input,select{{width:100%;background:#0a111e;color:#edf5ff;border:1px solid #263750;border-radius:14px;padding:13px 14px;font:inherit}}.meta{{display:flex;gap:8px;flex-wrap:wrap;margin:15px 0}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:11px}}.card{{border:1px solid #22324b;background:#0b1220;border-radius:18px;padding:16px;transition:.18s transform,.18s border-color}}.card:hover{{transform:translateY(-2px);border-color:#3b5b82}}.top{{display:flex;justify-content:space-between;gap:10px;align-items:center}}.name{{font-size:19px;font-weight:900}}.rank{{color:#6f829f;font-size:11px}}.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:13px}}.s{{background:#09101a;border-radius:11px;padding:9px}}.s b{{display:block;font-size:15px}}.s span{{color:#71839f;font-size:8px;letter-spacing:.08em}}.empty{{padding:30px;text-align:center;color:#8fa0ba;display:none}}@media(max-width:860px){{.grid{{grid-template-columns:1fr 1fr}}}}@media(max-width:580px){{.grid{{grid-template-columns:1fr}}.toolbar{{grid-template-columns:1fr}}}}</style></head><body><main><a href="../">← Meta Forge</a><section class="hero"><span class="badge">{len(heroes)} HÉROES · PATCH {patch}</span><h1>Live Roster</h1><p>Vista estadística completa del snapshot público sincronizado. WR, ban y pick son datos del snapshot. Las fichas marcadas como <strong>Editorial</strong> tienen además análisis estratégico curado en Meta Forge.</p><div class="meta"><span class="pill live">LIVE STATS · WR / BAN / PICK</span><span class="pill editorial">EDITORIAL · SOLO DONDE ESTÁ CURADO</span></div><p>Fuente declarada: {source} · consultado {fetched}</p></section><div class="toolbar"><input id="q" type="search" placeholder="Buscar héroe…" aria-label="Buscar héroe"><select id="sort" aria-label="Ordenar"><option value="wr">Mayor win rate</option><option value="ban">Mayor ban rate</option><option value="pick">Mayor pick rate</option><option value="name">Nombre A-Z</option></select></div><div id="grid" class="grid"></div><div id="empty" class="empty">No encontramos héroes con ese nombre.</div></main><script>const HEROES={data};const grid=document.getElementById('grid'),q=document.getElementById('q'),sort=document.getElementById('sort'),empty=document.getElementById('empty');function p(v){{return Number.isFinite(v)?v.toFixed(2)+'%':'—'}}function render(){{let rows=HEROES.filter(h=>h.name.toLowerCase().includes(q.value.trim().toLowerCase()));const key=sort.value;rows.sort((a,b)=>key==='name'?a.name.localeCompare(b.name):(Number(b[key]??-1)-Number(a[key]??-1)));grid.innerHTML=rows.map((h,i)=>`<a class="card" href="../stats/heroes/${{h.slug}}/"><div class="top"><span class="name">${{h.name}}</span><span class="rank">${{h.editorial?'EDITORIAL + LIVE':'LIVE'}} · #${{i+1}}</span></div><div class="stats"><div class="s"><b>${{p(h.wr)}}</b><span>WIN RATE</span></div><div class="s"><b>${{p(h.ban)}}</b><span>BAN</span></div><div class="s"><b>${{p(h.pick)}}</b><span>PICK</span></div></div></a>`).join('');empty.style.display=rows.length?'none':'block'}}q.addEventListener('input',render);sort.addEventListener('change',render);render();</script></body></html>''',encoding='utf-8')

    # Add a clear homepage entry without disturbing existing interactive modules.
    if INDEX.exists():
        html=INDEX.read_text(encoding='utf-8')
        if 'href="roster/"' not in html:
            marker='<div id="homeQuickActions" class="quick-actions">'
            link='<a href="roster/" class="quick-action"><strong>Live Roster</strong><span>133 héroes · WR, ban y pick →</span></a>'
            if marker in html:html=html.replace(marker,marker+link,1)
            else:html=html.replace('<main>','<main>'+link,1)
            INDEX.write_text(html,encoding='utf-8')

    # Extend sitemap with full statistical coverage.
    if SITEMAP.exists():
        sm=SITEMAP.read_text(encoding='utf-8')
        additions=[BASE+'roster/']+[BASE+'stats/heroes/'+slugify(h['name'])+'/' for h in heroes]
        new=''.join(f'<url><loc>{escape(u)}</loc></url>' for u in additions if u not in sm)
        if new:sm=sm.replace('</urlset>',new+'</urlset>')
        SITEMAP.write_text(sm,encoding='utf-8')
    print(f'Generated full live roster and {len(heroes)} statistical hero pages')

if __name__=='__main__':main()
