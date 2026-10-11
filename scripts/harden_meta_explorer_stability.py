from pathlib import Path

PAGE = Path('explore/index.html')
if not PAGE.exists():
    raise RuntimeError('Meta Explorer page missing')

page = PAGE.read_text(encoding='utf-8')

# 1) Turn redraw completion into an explicit event and debounce search redraws.
old_draw_tail = "state()}xs.addEventListener('change',draw);ys.addEventListener('change',draw);search.addEventListener('input',draw);"
new_draw_tail = "state();svg.dispatchEvent(new CustomEvent('mf:explorer-drawn'))}xs.addEventListener('change',draw);ys.addEventListener('change',draw);let explorerSearchFrame=0;search.addEventListener('input',()=>{cancelAnimationFrame(explorerSearchFrame);explorerSearchFrame=requestAnimationFrame(draw)});"
if old_draw_tail not in page:
    raise RuntimeError('Explorer draw/search hook not found')
page = page.replace(old_draw_tail, new_draw_tail, 1)

# 2) Power tools no longer watch DOM mutations; they react once per completed redraw.
old_power = "const observer=new MutationObserver(()=>syncVisibility());if(svg)observer.observe(svg,{childList:true});"
new_power = "if(svg)svg.addEventListener('mf:explorer-drawn',syncVisibility);"
if old_power not in page:
    raise RuntimeError('Explorer power-tools observer hook not found')
page = page.replace(old_power, new_power, 1)

# 3) Keyboard/accessibility upgrade follows the same explicit redraw event.
old_keyboard = "upgrade();new MutationObserver(upgrade).observe(svg,{childList:true});"
new_keyboard = "upgrade();svg.addEventListener('mf:explorer-drawn',upgrade);"
if old_keyboard not in page:
    raise RuntimeError('Explorer keyboard observer hook not found')
page = page.replace(old_keyboard, new_keyboard, 1)

# Small runtime marker for QA/debugging without adding another observer/listener loop.
marker = '<meta name="mf-explorer-stability" content="event-driven-v1">'
if marker not in page:
    page = page.replace('</head>', marker + '</head>', 1)

PAGE.write_text(page, encoding='utf-8')
print('Meta Explorer stability hardened: mutation_observers=0; redraw_event=mf:explorer-drawn; search=raf_debounced')
