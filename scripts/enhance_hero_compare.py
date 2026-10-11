from pathlib import Path

p=Path('compare/index.html')
if not p.exists():
    raise RuntimeError('compare/index.html missing')
html=p.read_text(encoding='utf-8')
if 'id="swapHeroes"' in html:
    print('Hero Compare explanation already enhanced')
    raise SystemExit

# Add swap action next to share.
needle='<button id="share" type="button">Copiar enlace</button>'
replace='<button id="swapHeroes" type="button" aria-label="Intercambiar héroes">⇄ Intercambiar</button>'+needle
if needle not in html:
    raise RuntimeError('Hero Compare share button marker missing')
html=html.replace(needle,replace,1)

# Give the controls enough columns for swap + share on desktop.
html=html.replace('grid-template-columns:1fr auto 1fr auto;gap:10px','grid-template-columns:1fr auto 1fr auto auto;gap:10px',1)

# Add a visual divider for score components.
css='.component-title{margin:10px 0 2px;padding:12px 4px 4px;border-top:1px solid #283952;color:#a995ff;font-size:10px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.component-note{margin:2px 4px 8px;color:#71849f;font-size:9px}'
html=html.replace('</style>',css+'</style>',1)

old="rows.innerHTML=metric('WR','wr',pct)+metric('Ban','ban',pct)+metric('Pick','pick',pct)+metric('Meta Score','score',num)+metric('Momentum','momentum',mom)+metric('Ranking','rank',v=>Number.isFinite(v)?'#'+v:'—',true);"
new="rows.innerHTML=metric('WR','wr',pct)+metric('Ban','ban',pct)+metric('Pick','pick',pct)+metric('Meta Score','score',num)+metric('Momentum','momentum',mom)+metric('Ranking','rank',v=>Number.isFinite(v)?'#'+v:'—',true)+'<div class=\"component-title\">Por qué cambia el Meta Score</div><div class=\"component-note\">Percentiles relativos al roster live completo. Más alto = mayor señal en ese componente.</div>'+metric('Percentil WR','wr_pct',num)+metric('Percentil Pick','pick_pct',num)+metric('Percentil Ban','ban_pct',num)+metric('Percentil Momentum','momentum_pct',num);"
if old not in html:
    raise RuntimeError('Hero Compare render metrics marker missing')
html=html.replace(old,new,1)

# Prevent accidental same-vs-same comparisons and add side swap.
old_events="sa.onchange=render;sb.onchange=render;document.getElementById('share').onclick="
new_events="function avoidSame(changed){if(sa.value!==sb.value)return;const other=HEROES.find(h=>h.name!==sa.value);if(!other)return;if(changed==='a')sb.value=other.name;else sa.value=other.name}sa.onchange=()=>{avoidSame('a');render()};sb.onchange=()=>{avoidSame('b');render()};document.getElementById('swapHeroes').onclick=()=>{const x=sa.value;sa.value=sb.value;sb.value=x;render()};document.getElementById('share').onclick="
if old_events not in html:
    raise RuntimeError('Hero Compare event marker missing')
html=html.replace(old_events,new_events,1)

p.write_text(html,encoding='utf-8')
print('Enhanced Hero Compare with score component explanation, distinct selection and swap action')
