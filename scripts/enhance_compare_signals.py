from pathlib import Path

PAGE=Path('compare/index.html')
if not PAGE.exists():
    raise RuntimeError('compare/index.html is required for compare signal summary')
page=PAGE.read_text(encoding='utf-8')
if 'id="compareSignalSummary"' in page:
    print('Compare signal summary already injected')
    raise SystemExit(0)
if 'const HEROES=' not in page or 'id="rows"' not in page:
    raise RuntimeError('Base Hero Compare runtime missing')
CSS='''<style id="compare-signal-style">.signal-summary{margin-top:14px;padding:15px;border:1px solid #2a3d58;border-radius:16px;background:#09131f}.signal-summary h2{margin:3px 0 8px;font-size:17px}.signal-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.signal-item{padding:10px;border:1px solid #243650;border-radius:12px;background:#0c1625}.signal-item b{display:block;font-size:11px}.signal-item span{display:block;margin-top:4px;color:#8294ad;font-size:10px;line-height:1.45}.signal-foot{margin:9px 0 0;color:#73849f;font-size:9px;line-height:1.5}@media(max-width:650px){.signal-grid{grid-template-columns:1fr}}</style>'''
PANEL='''<section id="compareSignalSummary" class="signal-summary"><small>LECTURA RÁPIDA</small><h2>Qué diferencia realmente a esta pareja</h2><div id="compareSignalGrid" class="signal-grid"></div><p class="signal-foot">Las diferencias son descriptivas del snapshot actual. No convierten WR, pick, ban o Meta Score en una recomendación automática de pick.</p></section>'''
marker='<div class="note">Meta Score = señal estadística compuesta'
idx=page.find(marker)
if idx==-1:
    raise RuntimeError('Hero Compare note marker missing')
page=page[:idx]+PANEL+page[idx:]
JS=r'''<script id="compare-signal-script">(()=>{const box=document.getElementById('compareSignalGrid'),a=document.getElementById('a'),b=document.getElementById('b');if(!box||!a||!b||typeof by==='undefined')return;const pp=v=>`${v>0?'+':''}${v.toFixed(2)} pp`,pts=v=>`${v>0?'+':''}${v.toFixed(1)} pts`;function line(title,text){return `<div class="signal-item"><b>${title}</b><span>${text}</span></div>`}function winner(x,y,key){const d=(Number(x?.[key])||0)-(Number(y?.[key])||0);return {d,hi:d>=0?x:y,lo:d>=0?y:x}}function render(){const x=by.get(a.value),y=by.get(b.value);if(!x||!y)return;const wr=winner(x,y,'wr'),pick=winner(x,y,'pick'),ban=winner(x,y,'ban'),score=winner(x,y,'score');const parts=[];parts.push(line('Win rate',Math.abs(wr.d)<.01?'Prácticamente empatados en WR.':`${wr.hi.name} marca ${pp(Math.abs(wr.d))} sobre ${wr.lo.name} en WR.`));parts.push(line('Presencia',Math.abs(pick.d)<.01?'Pick rate prácticamente igual.':`${pick.hi.name} aparece ${pp(Math.abs(pick.d))} más en pick rate.`));parts.push(line('Presión de ban',Math.abs(ban.d)<.01?'Ban rate prácticamente igual.':`${ban.hi.name} recibe ${pp(Math.abs(ban.d))} más de ban rate.`));parts.push(line('Meta Score',Math.abs(score.d)<.05?'Meta Score prácticamente empatado.':`${score.hi.name} está ${pts(Math.abs(score.d))} por encima en Meta Score estadístico.`));const xm=x.momentum_observed===true,ym=y.momentum_observed===true;if(xm&&ym&&Number.isFinite(x.momentum)&&Number.isFinite(y.momentum)){const m=winner(x,y,'momentum');parts.push(line('Momentum',Math.abs(m.d)<.0005?'Momentum prácticamente empatado.':`${m.hi.name} tiene mayor señal de momentum en este corte.`))}else parts.push(line('Momentum','Aún no hay historial suficiente para interpretar momentum de forma fiable.'));box.innerHTML=parts.join('')}a.addEventListener('change',()=>queueMicrotask(render));b.addEventListener('change',()=>queueMicrotask(render));render()})();</script>'''
page=page.replace('</head>',CSS+'</head>',1)
page=page.replace('</body>',JS+'</body>',1)
PAGE.write_text(page,encoding='utf-8')
print('Enhanced Hero Compare with neutral signal summary and explicit no-pick-recommendation framing')
