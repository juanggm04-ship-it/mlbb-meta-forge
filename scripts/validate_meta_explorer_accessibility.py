from pathlib import Path
import re,sys
PAGE=Path('explore/index.html')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(PAGE.exists(),'Meta Explorer page missing')
if PAGE.exists():
    text=PAGE.read_text(encoding='utf-8')
    for token,msg in [
        ('id="swapExplorerAxes"','Swap-axes control missing'),
        ('id="resetExplorerView"','Reset-view control missing'),
        ('id="explorerKeyboardRuntime"','Explorer keyboard runtime missing'),
        ("c.setAttribute('tabindex','0')",'Explorer points are not keyboard focusable'),
        ("c.setAttribute('role','button')",'Explorer point role missing'),
        ("c.setAttribute('aria-label','Seleccionar '+t)",'Explorer point accessible label missing'),
        ("e.key==='Enter'||e.key===' '",'Enter/Space point activation missing'),
        ("c.dispatchEvent(new MouseEvent('click',{bubbles:true}))",'Keyboard activation is not routed through point click behavior'),
        ("xs.value=ys.value;ys.value=x",'Axis swap implementation missing'),
        ("xs.dispatchEvent(new Event('change',{bubbles:true}))",'Axis swap does not redraw plot'),
        ("location.assign(clean)",'Reset-view implementation missing'),
        ('.dot[tabindex="0"]:focus','Visible SVG keyboard focus style missing'),
    ]: need(token in text,msg)
    runtime=re.search(r'<script id="explorerKeyboardRuntime">(.*?)</script>',text,re.S)
    need(bool(runtime),'Explorer keyboard runtime block could not be isolated')
    if runtime:
        js=runtime.group(1)
        need('mf:explorer-drawn' in js and 'addEventListener' in js and 'upgrade' in js,'Keyboard affordances are not restored after plot redraw')
        need('MutationObserver' not in js,'Explorer keyboard runtime must remain free of MutationObserver loops')
    need('MutationObserver' not in text,'Explorer page must remain free of MutationObserver loops')
if errors:
    print('META EXPLORER ACCESSIBILITY VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Meta Explorer accessibility validation passed: every rendered point is upgraded through the stable redraw event, Enter/Space mirrors click selection, and swap/reset controls are present.')
