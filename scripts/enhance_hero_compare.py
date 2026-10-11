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

# Add visual language for score components and neutral momentum.
css='.component-title{margin:10px 0 2px;padding:12px 4px 4px;border-top:1px solid #283952;color:#a995ff;font-size:10px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}.component-note{margin:2px 4px 8px;color:#71849f;font-size:9px}.neutral-value{color:#ffd36c}.neutral-label{color:#c9a64d}.momentum-neutral-note{padding:9px 11px;border:1px solid #493f25;border-radius:10px;background:#17150d;color:#bda968;font-size:9px;line-height:1.45}'
html=html.replace('</style>',css+'</style>',1)

# Add a custom momentum percentile row. Neutral 50 is shown but never highlighted as a winner.
marker="function render(){const a=by.get(sa.value),b=by.get(sb.value);if(!a||!b)return;"
helper="function momentumPercentile(){const a=by.get(sa.value),b=by.get(sb.value);const av=a.momentum_pct,bv=b.momentum_pct;const ao=!!a.momentum_observed,bo=!!b.momentum_observed;if(ao&&bo)return metric('Percentil Momentum','momentum_pct',num);const left=ao?num(av):num(av)+' · neutral',right=bo?num(bv):num(bv)+' · neutral';return `<div class=\"row\"><strong class=\"${ao?'':'neutral-value'}\">${left}</strong><span class=\"label ${ao&&bo?'':'neutral-label'}\">Percentil Momentum</span><strong class=\"${bo?'':'neutral-value'}\">${right}</strong></div><div class=\"momentum-neutral-note\">“Neutral” significa percentil 50 asignado por falta de historial válido. No significa que el héroe no haya cambiado.</div>`}"
if marker not in html:
    raise RuntimeError('Hero Compare render marker missing')
html=html.replace(marker,helper+marker,1)

old="rows.innerHTML=metric('WR','wr',pct)+metric('Ban','ban',pct)+metric('Pick','pick',pct)+metric('Meta Score','score',num)+metric('Momentum','momentum',mom)+metric('Ranking','rank',v=>Number.isFinite(v)?'#'+v:'—',true);"
new="rows.innerHTML=metric('WR','wr',pct)+metric('Ban','ban',pct)+metric('Pick','pick',pct)+metric('Meta Score','score',num)+metric('Momentum observado','momentum',mom)+metric('Ranking','rank',v=>Number.isFinite(v)?'#'+v:'—',true)+'<div class=\"component-title\">Por qué cambia el Meta Score</div><div class=\"component-note\">Percentiles relativos al roster live completo. Más alto = mayor señal en ese componente. Momentum neutral no es tendencia observada.</div>'+metric('Percentil WR','wr_pct',num)+metric('Percentil Pick','pick_pct',num)+metric('Percentil Ban','ban_pct',num)+momentumPercentile();"
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
print('Enhanced Hero Compare with score explanation, swap, distinct selection and explicit neutral momentum state')
