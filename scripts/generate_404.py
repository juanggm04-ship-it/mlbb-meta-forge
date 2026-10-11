from pathlib import Path
from html import escape
from site_config import load_site_config

CFG=load_site_config()
BASE=CFG['base_url']
SITE=escape(CFG['site_name'])

html=f'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#070a12">
  <meta name="description" content="La ruta que buscas no existe en {SITE}. Vuelve al meta, al roster o a las herramientas de análisis.">
  <title>404 · Ruta no encontrada | {SITE}</title>
  <style>
    :root{{--bg:#070a12;--panel:#0d1423;--line:#243452;--text:#eef5ff;--muted:#9bacbf;--cyan:#51e4ff;--violet:#9b78ff}}
    *{{box-sizing:border-box}}
    body{{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;background:radial-gradient(circle at 15% 10%,#15264a 0,transparent 31%),radial-gradient(circle at 88% 88%,#21133d 0,transparent 34%),var(--bg);color:var(--text);font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    main{{width:min(820px,100%);padding:clamp(26px,5vw,54px);border:1px solid var(--line);border-radius:30px;background:linear-gradient(145deg,#10192aaa,#0a101dcc);box-shadow:0 30px 90px #0008;backdrop-filter:blur(18px)}}
    .code{{font-size:clamp(82px,22vw,190px);font-weight:950;line-height:.78;letter-spacing:-.08em;background:linear-gradient(110deg,var(--cyan),var(--violet));-webkit-background-clip:text;background-clip:text;color:transparent}}
    .eyebrow{{display:inline-flex;margin:0 0 18px;padding:7px 10px;border:1px solid #51e4ff55;border-radius:999px;color:var(--cyan);font-size:11px;font-weight:900;letter-spacing:.1em}}
    h1{{margin:24px 0 10px;font-size:clamp(30px,6vw,58px);line-height:1;letter-spacing:-.05em}}
    p{{max-width:620px;margin:0;color:var(--muted);font-size:16px;line-height:1.7}}
    nav{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:30px}}
    a{{display:flex;min-height:54px;align-items:center;justify-content:center;padding:12px 14px;border:1px solid var(--line);border-radius:14px;background:#111b2d;color:var(--text);font-weight:850;text-decoration:none;transition:transform .16s ease,border-color .16s ease,background .16s ease}}
    a:hover,a:focus-visible{{transform:translateY(-2px);border-color:#51e4ffaa;background:#142238;outline:none}}
    a.primary{{background:linear-gradient(115deg,var(--cyan),#8c75ff);color:#06101b;border-color:transparent}}
    .hint{{margin-top:22px;font-size:12px;color:#70829d}}
    @media(max-width:650px){{nav{{grid-template-columns:1fr 1fr}}main{{border-radius:22px}}}}
    @media(max-width:380px){{nav{{grid-template-columns:1fr}}}}
    @media(prefers-reduced-motion:reduce){{a{{transition:none}}}}
  </style>
</head>
<body>
  <main id="main-content">
    <span class="eyebrow">RUTA FUERA DEL MAPA</span>
    <div class="code" aria-hidden="true">404</div>
    <h1>Ese enlace no está en el draft.</h1>
    <p>La página pudo moverse, el enlace puede estar incompleto o quizá llegaste a una ruta que nunca existió. El resto de Meta Forge sigue listo para jugar.</p>
    <nav aria-label="Volver a Meta Forge">
      <a class="primary" href="{BASE}">Inicio</a>
      <a href="{BASE}roster/">Live Roster</a>
      <a href="{BASE}explore/">Explorer</a>
      <a href="{BASE}compare/">Compare</a>
    </nav>
    <p class="hint">Error 404 · Esta página no se incluye en el índice de buscadores.</p>
  </main>
</body>
</html>'''

Path('404.html').write_text(html,encoding='utf-8')
print(f'404 page generated: base={BASE}; branded=true; noindex_managed_by_seo=true')
