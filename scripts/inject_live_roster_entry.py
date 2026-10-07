from pathlib import Path

p=Path('index.html')
html=p.read_text(encoding='utf-8')
if 'href="roster/"' in html:
    print('Live Roster entry already present')
    raise SystemExit

link='<a href="roster/" class="quick-action"><strong>Live Roster</strong><span>133 héroes · WR, ban y pick →</span></a>'
marker='<div id="homeQuickActions" class="quick-actions">'
if marker not in html:
    raise RuntimeError('homeQuickActions not found; cannot add Live Roster entry safely')
html=html.replace(marker,marker+link,1)
p.write_text(html,encoding='utf-8')
print('Injected Live Roster homepage entry')
