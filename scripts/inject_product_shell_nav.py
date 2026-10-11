from pathlib import Path
import re

TARGETS={
    Path('roster/index.html'):('roster','../'),
    Path('trends/index.html'):('trends','../'),
    Path('compare/index.html'):('compare','../'),
    Path('my-meta/index.html'):('my-meta','../'),
}

CSS='''<style id="product-shell-nav-style">
.product-shell-nav{width:min(1180px,calc(100% - 28px));margin:14px auto 0;display:flex;align-items:center;gap:12px;padding:8px;border:1px solid #263954;border-radius:16px;background:#08111ddd;backdrop-filter:blur(14px);box-shadow:0 12px 35px #0004;position:relative;z-index:80}.ps-brand{display:flex;align-items:center;gap:8px;padding:8px 10px;color:#eef6ff!important;text-decoration:none!important;font-size:12px;font-weight:950;letter-spacing:.04em;white-space:nowrap}.ps-mark{width:25px;height:25px;border-radius:8px;display:grid;place-items:center;background:linear-gradient(135deg,#50e4ff,#8f78ff);color:#07101b;font-size:11px;box-shadow:0 0 18px #50e4ff30}.ps-links{display:flex;gap:3px;align-items:center;margin-left:auto;overflow:auto;scrollbar-width:none}.ps-links::-webkit-scrollbar{display:none}.ps-links a{padding:8px 10px;border-radius:9px;color:#8799b6!important;text-decoration:none!important;font-size:10px;font-weight:850;white-space:nowrap}.ps-links a:hover,.ps-links a:focus-visible{background:#101c2d;color:#edf5ff!important;outline:none}.ps-links a[aria-current="page"]{background:#13223a;color:#65e5ff!important;box-shadow:inset 0 0 0 1px #335170}.ps-method{border-left:1px solid #253650;margin-left:3px;padding-left:12px!important}@media(max-width:680px){.product-shell-nav{width:calc(100% - 20px);gap:4px}.ps-brand{padding:6px}.ps-brand-text{display:none}.ps-links{margin-left:0}.ps-links a{padding:8px 9px}}
</style>'''

changed=0
for path,(current,root) in TARGETS.items():
    if not path.exists():
        raise RuntimeError(f'Missing product navigation target: {path}')
    html=path.read_text(encoding='utf-8')
    if 'id="productShellNav"' in html:
        continue
    def link(slug,label,url):
        cur=' aria-current="page"' if current==slug else ''
        return f'<a href="{url}"{cur}>{label}</a>'
    nav=(f'<nav id="productShellNav" class="product-shell-nav" aria-label="Navegación de Meta Forge">'
         f'<a class="ps-brand" href="{root}"><span class="ps-mark">M</span><span class="ps-brand-text">MLBB FORGE</span></a>'
         f'<div class="ps-links">'
         f'{link("roster","Roster",root+"roster/")}'
         f'{link("trends","Trends",root+"trends/")}'
         f'{link("compare","Comparar",root+"compare/")}'
         f'{link("my-meta","Mi Meta",root+"my-meta/")}'
         f'<a class="ps-method" href="{root}methodology.html">Metodología</a>'
         f'</div></nav>')
    if '</head>' not in html:
        raise RuntimeError(f'No </head> in {path}')
    html=html.replace('</head>',CSS+'</head>',1)
    match=re.search(r'<body(?:\s[^>]*)?>',html,re.I)
    if not match:
        raise RuntimeError(f'No body tag in {path}')
    pos=match.end()
    html=html[:pos]+nav+html[pos:]
    path.write_text(html,encoding='utf-8')
    changed+=1

if changed not in (0,len(TARGETS)):
    raise RuntimeError(f'Product shell navigation injected into only {changed}/{len(TARGETS)} targets')
print(f'Product shell navigation ready across {len(TARGETS)} core tool pages')
